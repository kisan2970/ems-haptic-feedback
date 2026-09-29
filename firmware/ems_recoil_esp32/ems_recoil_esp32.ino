/*
 * ems_recoil_esp32.ino  -  EMS 가상 충돌/반동 시뮬레이터 펌웨어 (ESP32 DevKit V1, 30핀)
 * 보드: ESP32 Dev Module / DOIT ESP32 DEVKIT V1 (WROOM-32), Serial 115200
 * 프로토콜은 우노 버전(ems_recoil.ino)과 동일. Processing 코드 수정 불필요 (포트만 변경).
 *
 * 핀 배치 (스트래핑 핀 0/2(입력)/5/12/15 회피, 부팅 시 글리치 없는 핀만 출력에 사용)
 *  GPIO26  E-STOP   비상정지 NO접점 -> GND (INPUT_PULLUP, LOW=눌림, 인터럽트)
 *  GPIO27  ARM      키스위치 -> GND (LOW=자극 허용)
 *  GPIO17  TRIG1    TLC555 트리거 CH1 (평소 HIGH, 시작 시 100us LOW)
 *  GPIO16  GATE1    Q1 베이스 CH1 (HIGH=자극)  ** 외부 10k 풀다운 필수 **
 *  GPIO18  GATE2    Q2 베이스 CH2              ** 외부 10k 풀다운 필수 **
 *  GPIO19  TRIG2    TLC555 트리거 CH2
 *  GPIO25  BUZZ     부저
 *  GPIO2   LED      보드 내장 LED (ARMED/STIM 시 점등)
 *  GPIO21/22 I2C    MPU-6050 SDA/SCL
 *
 * 3.3V 로직 주의: TLC555는 ESP32 3V3 핀에서 전원, SSR LED 직렬저항 150Ω.
 */
#include <Wire.h>
#include <esp_task_wdt.h>
#include "soc/gpio_reg.h"
#include "soc/soc.h"

#define PIN_ESTOP 26
#define PIN_ARM   27
#define PIN_TRIG1 17
#define PIN_GATE1 16
#define PIN_GATE2 18
#define PIN_TRIG2 19
#define PIN_BUZZ  25
#define PIN_LED   2
#define PIN_SDA   21
#define PIN_SCL   22

// ---------- 펌웨어 안전 클램프 (하드웨어 555 창 0.33s보다 항상 작게) ----------
const uint16_t MAX_PULSE_MS     = 250;
const uint16_t MIN_GAP_MS       = 300;
const uint16_t HEARTBEAT_TO_MS  = 1000;
const uint32_t DUTY_WINDOW_MS   = 10000;
const uint16_t MAX_ON_IN_WINDOW = 3000;   // 10초 중 누적 3초 (30%)
const uint8_t  MAX_TRIG_PER_MIN = 30;
const uint8_t  MOD_PERIOD_MS    = 20;     // 듀티 변조 50Hz
const uint8_t  SENSOR_HZ        = 100;
const uint32_t WDT_TIMEOUT_MS   = 250;

enum State : uint8_t { ST_IDLE = 0, ST_ARMED = 1, ST_STIM = 2, ST_COOL = 3, ST_FAULT = 9 };
volatile State state = ST_IDLE;
volatile bool  estopFlag = false;

struct Stim { uint8_t ch; uint16_t dur; uint8_t duty; uint8_t env; uint32_t t0; } cur;
uint32_t lastStimEnd = 0, lastHeartbeat = 0;

const uint8_t LOG_N = 32;
uint32_t logT[LOG_N]; uint16_t logD[LOG_N]; uint8_t logI = 0;

float roll = 0, pitch = 0;
bool imuOK = false;
uint32_t lastSensor = 0; uint16_t seq = 0;
char rx[64]; uint8_t rxLen = 0;

// ---------- 유틸 ----------
void gatesOff() { digitalWrite(PIN_GATE1, LOW); digitalWrite(PIN_GATE2, LOW); }

// 인터럽트 안전 차단: 레지스터 직접 쓰기 (IRAM에서 실행)
void IRAM_ATTR estopISR() {
  REG_WRITE(GPIO_OUT_W1TC_REG, (1UL << PIN_GATE1) | (1UL << PIN_GATE2));
  estopFlag = true;
}

void sendLine(const char* body) {
  uint8_t cs = 0; for (const char* p = body; *p; p++) cs ^= *p;
  char out[112];
  snprintf(out, sizeof out, "$%s*%02X", body, cs);
  Serial.println(out);
}

void enterFault(uint8_t code) {
  gatesOff(); state = ST_FAULT;
  char b[24]; snprintf(b, sizeof b, "E,%u,FAULT", code); sendLine(b);
  tone(PIN_BUZZ, 2000, 800);
}

// ---------- MPU-6050 ----------
bool mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(0x68); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission() == 0;
}
void mpuInit() {
  imuOK = mpuWrite(0x6B, 0x00);   // wake
  mpuWrite(0x1C, 0x10);           // accel +-8g  (4096 LSB/g)
  mpuWrite(0x1B, 0x10);           // gyro  +-1000 dps (32.8 LSB/dps)
  mpuWrite(0x1A, 0x03);           // DLPF 44Hz
}
void sensorTick() {
  static uint32_t tPrev = micros();
  int16_t ax = 0, ay = 0, az = 4096, gx = 0, gy = 0, gz = 0;
  if (imuOK) {
    Wire.beginTransmission(0x68); Wire.write(0x3B); Wire.endTransmission(false);
    if (Wire.requestFrom(0x68, 14) == 14) {
      ax = Wire.read() << 8 | Wire.read(); ay = Wire.read() << 8 | Wire.read(); az = Wire.read() << 8 | Wire.read();
      Wire.read(); Wire.read();
      gx = Wire.read() << 8 | Wire.read(); gy = Wire.read() << 8 | Wire.read(); gz = Wire.read() << 8 | Wire.read();
    }
  }
  uint32_t tNow = micros(); float dt = (tNow - tPrev) * 1e-6f; tPrev = tNow;
  float axg = ax / 4096.0f, ayg = ay / 4096.0f, azg = az / 4096.0f;
  float gxd = gx / 32.8f,   gyd = gy / 32.8f,   gzd = gz / 32.8f;
  float rollA  = atan2f(ayg, azg) * 57.2958f;
  float pitchA = atan2f(-axg, sqrtf(ayg * ayg + azg * azg)) * 57.2958f;
  roll  = 0.98f * (roll  + gxd * dt) + 0.02f * rollA;
  pitch = 0.98f * (pitch + gyd * dt) + 0.02f * pitchA;

  char b[100];
  snprintf(b, sizeof b, "S,%u,%.1f,%.1f,%d,%d,%d,%d,%d,%d,%d,%u",
           seq++, roll, pitch, (int)gxd, (int)gyd, (int)gzd,
           (int)(axg * 100), (int)(ayg * 100), (int)(azg * 100),
           -1, (unsigned)state);
  sendLine(b);
}

// ---------- 자극 ----------
bool budgetOK(uint32_t now, uint16_t dur) {
  uint32_t on = 0; uint8_t cnt = 0;
  for (uint8_t i = 0; i < LOG_N; i++) {
    if (!logT[i]) continue;
    if (now - logT[i] < DUTY_WINDOW_MS) on += logD[i];
    if (now - logT[i] < 60000UL) cnt++;
  }
  return (on + dur <= MAX_ON_IN_WINDOW) && (cnt < MAX_TRIG_PER_MIN);
}

void startStim(int ch, int dur, int duty, int env) {
  uint32_t now = millis();
  if (state != ST_ARMED) { sendLine("E,4,NOT_ARMED"); return; }
  if (ch != 1 && ch != 2) { sendLine("E,10,BAD_CH"); return; }
  dur  = constrain(dur, 10, MAX_PULSE_MS);
  duty = constrain(duty, 10, 100);
  if (!budgetOK(now, dur)) { sendLine("E,5,BUDGET"); return; }

  cur = { (uint8_t)ch, (uint16_t)dur, (uint8_t)duty, (uint8_t)env, now };
  logT[logI] = now ? now : 1; logD[logI] = dur; logI = (logI + 1) % LOG_N;

  uint8_t tp = (ch == 2) ? PIN_TRIG2 : PIN_TRIG1;
  digitalWrite(tp, LOW); delayMicroseconds(100); digitalWrite(tp, HIGH);   // 555 창 열기
  digitalWrite(ch == 2 ? PIN_GATE2 : PIN_GATE1, HIGH);
  state = ST_STIM;
  char b[32]; snprintf(b, sizeof b, "K,T,%d,%d,%d", ch, dur, duty); sendLine(b);
}

// ---------- 시리얼 파서 ----------
bool checksumOK(char* line, char** body) {
  if (line[0] != '$') return false;
  char* star = strchr(line, '*'); if (!star) return false;
  uint8_t cs = 0; for (char* p = line + 1; p < star; p++) cs ^= *p;
  uint8_t given = strtoul(star + 1, NULL, 16);
  *star = 0; *body = line + 1;
  return cs == given;
}

void handleLine(char* line) {
  char* body;
  if (!checksumOK(line, &body)) { sendLine("E,6,BAD_CS"); return; }
  lastHeartbeat = millis();
  switch (body[0]) {
    case 'H': break;
    case 'X': gatesOff(); if (state != ST_FAULT) state = ST_IDLE; sendLine("K,X"); break;
    case 'A': {
      int v = atoi(body + 2);
      if (v == 1) {
        if (state == ST_FAULT)                 sendLine("E,7,IN_FAULT");
        else if (digitalRead(PIN_ARM) == HIGH) sendLine("E,2,ARM_SWITCH_OFF");
        else { state = ST_ARMED; sendLine("K,A,1"); }
      } else { gatesOff(); if (state != ST_FAULT) state = ST_IDLE; sendLine("K,A,0"); }
    } break;
    case 'T': {
      int ch = 1, dur = 0, duty = 100, env = 0;
      sscanf(body, "T,%d,%d,%d,%d", &ch, &dur, &duty, &env);
      startStim(ch, dur, duty, env);
    } break;
    case 'R':
      if (state == ST_FAULT && digitalRead(PIN_ESTOP) == HIGH) { estopFlag = false; state = ST_IDLE; sendLine("K,R"); }
      else sendLine("E,8,ESTOP_STILL_PRESSED");
      break;
    default: sendLine("E,9,UNKNOWN");
  }
}

void readSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '$') { rxLen = 0; rx[rxLen++] = c; }
    else if (c == '\n' || c == '\r') { if (rxLen) { rx[rxLen] = 0; handleLine(rx); rxLen = 0; } }
    else if (rxLen && rxLen < sizeof(rx) - 1) rx[rxLen++] = c;
  }
}

// ---------- setup / loop ----------
void setup() {
  pinMode(PIN_GATE1, OUTPUT); pinMode(PIN_GATE2, OUTPUT); gatesOff();   // 가장 먼저 OFF
  pinMode(PIN_TRIG1, OUTPUT); digitalWrite(PIN_TRIG1, HIGH);
  pinMode(PIN_TRIG2, OUTPUT); digitalWrite(PIN_TRIG2, HIGH);
  pinMode(PIN_ESTOP, INPUT_PULLUP); pinMode(PIN_ARM, INPUT_PULLUP);
  pinMode(PIN_BUZZ, OUTPUT); pinMode(PIN_LED, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_ESTOP), estopISR, FALLING);

  Serial.begin(115200);
  Wire.begin(PIN_SDA, PIN_SCL, 400000);
  mpuInit();

  // 태스크 워치독: loop가 250ms 안에 돌지 않으면 패닉 리셋 -> 핀 Hi-Z -> 외부 풀다운으로 OFF
  esp_task_wdt_config_t cfg = { .timeout_ms = WDT_TIMEOUT_MS, .idle_core_mask = 0, .trigger_panic = true };
  if (esp_task_wdt_reconfigure(&cfg) != ESP_OK) esp_task_wdt_init(&cfg);
  esp_task_wdt_add(NULL);

  sendLine(imuOK ? "I,EMS_RECOIL,esp32-v1,MAXP=250,GAP=300,IMU=OK"
                 : "I,EMS_RECOIL,esp32-v1,MAXP=250,GAP=300,IMU=NONE");
}

void loop() {
  esp_task_wdt_reset();
  uint32_t now = millis();
  readSerial();

  if ((estopFlag || digitalRead(PIN_ESTOP) == LOW) && state != ST_FAULT) enterFault(1);
  if (state != ST_FAULT && state != ST_IDLE && digitalRead(PIN_ARM) == HIGH) {
    gatesOff(); state = ST_IDLE; sendLine("E,2,ARM_SWITCH_OFF");
  }
  if ((state == ST_ARMED || state == ST_STIM) && now - lastHeartbeat > HEARTBEAT_TO_MS) {
    gatesOff(); state = ST_IDLE; sendLine("E,3,HEARTBEAT_LOST");
  }

  if (state == ST_STIM) {
    uint32_t el = now - cur.t0;
    if (el >= cur.dur) { gatesOff(); lastStimEnd = now; state = ST_COOL; }
    else {
      uint8_t d = cur.duty;
      if (cur.env == 1) d = 100 - (uint32_t)(100 - cur.duty) * el / cur.dur;
      bool on = (d >= 100) || ((el % MOD_PERIOD_MS) < (uint32_t)MOD_PERIOD_MS * d / 100);
      digitalWrite(cur.ch == 2 ? PIN_GATE2 : PIN_GATE1, on ? HIGH : LOW);
    }
  } else if (state == ST_COOL && now - lastStimEnd >= MIN_GAP_MS) {
    state = ST_ARMED;
  }

  if (now - lastSensor >= 1000 / SENSOR_HZ) { lastSensor = now; sensorTick(); }
  digitalWrite(PIN_LED, (state == ST_ARMED || state == ST_STIM) ? HIGH : LOW);
}
