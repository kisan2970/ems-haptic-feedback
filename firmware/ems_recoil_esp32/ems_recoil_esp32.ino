/*
 * ems_recoil_esp32.ino  v2.1  -  EMS 근자극 기반 반동 + 무게감 피드백 펌웨어 (ESP32 DevKit V1, 30핀)
 * 보드: ESP32 Dev Module / DOIT ESP32 DEVKIT V1 (WROOM-32), Serial 115200, arduino-esp32 코어 3.x
 * 우노 v2.1(ems_recoil.ino)과 로직·프로토콜·안전 한계가 같다. 핀과 워치독·인터럽트만 다르다.
 * v1과 달리 유지 신호(KA)를 토글하므로 v2 회로(555 펄스 끊김 감지)에 그대로 쓸 수 있다.
 *
 * 핀 배치 (스트래핑 핀 0/2(입력)/5/12/15 회피, 부팅 시 글리치 없는 핀만 출력에 사용)
 *  GPIO26  E-STOP   비상정지 NO접점 -> GND (INPUT_PULLUP, LOW=눌림, 인터럽트)
 *  GPIO27  ARM      키스위치 -> GND (LOW=자극 허용)
 *  GPIO17  TRIG1    TLC555 트리거 CH1 (평소 HIGH, 시작 시 100us LOW)
 *  GPIO16  GATE1    Q1 베이스 CH1 (HIGH=자극)  ** 외부 10k 풀다운 필수 **
 *  GPIO18  GATE2    Q2 베이스 CH2              ** 외부 10k 풀다운 필수 **
 *  GPIO19  TRIG2    TLC555 트리거 CH2
 *  GPIO32  KA1      유지 신호 CH1 (우노 D9 자리. 100nF 결합 -> Q3)
 *  GPIO33  KA2      유지 신호 CH2 (우노 D10 자리. 100nF 결합 -> Q4)
 *  GPIO25  BUZZ     부저
 *  GPIO2   LED      보드 내장 LED (ARMED 시 점등)
 *  GPIO21/22 I2C    MPU-6050 SDA/SCL
 *
 * 3.3V 로직 주의: TLC555는 ESP32 3V3 핀에서 전원, SSR LED 직렬저항 150Ω.
 *   555를 3.3V로 돌려도 타이밍(470k x 100nF, 약 0.05s)은 전원 전압과 무관하다.
 *
 * 프로토콜·명령·오류 코드는 우노 펌웨어 머리말 참고.
 */
#include <Wire.h>
#include <esp_task_wdt.h>
#include "soc/gpio_reg.h"
#include "soc/soc.h"

#define PIN_ESTOP 26
#define PIN_ARM   27
#define PIN_BUZZ  25
#define PIN_LED   2
#define PIN_SDA   21
#define PIN_SCL   22
#define PIN_GATE1 16
#define PIN_GATE2 18
const uint32_t WDT_TIMEOUT_MS = 250;

// ---------- 안전 한계 ----------
const uint16_t MAX_PULSE_MS       = 250;    // 반동 1회 최대
const uint16_t MIN_GAP_MS         = 300;    // 반동 사이 최소 간격 (채널별)
const uint32_t PULSE_WINDOW_MS    = 10000;
const uint16_t MAX_PULSE_ON_WIN   = 3000;   // 10초 중 반동 누적 3초
const uint8_t  MAX_TRIG_PER_MIN   = 40;
const uint16_t HOLD_REFRESH_TO_MS = 200;    // $W 재전송 없으면 해제
const uint16_t MAX_HOLD_MS        = 5000;   // 한 번 들기 최대
const uint16_t HOLD_REST_MS       = 2000;   // 최대 도달 후 강제 휴식
const uint16_t HOLD_MIN_GAP_MS    = 500;    // 내려놓은 뒤 다시 들기까지 최소 간격
const uint16_t HOLD_SLOT_MS       = 10000;  // 무게 누적은 10초 칸 6개(최근 약 1분)에 시간으로 쌓는다
const uint8_t  HOLD_SLOTS         = 6;      //  -> 들기 횟수와 상관없이 누적 시간이 정확하다
const uint32_t MAX_HOLD_IN_WIN    = 30000;  // 1분 중 채널당 누적 30초
const uint16_t HEARTBEAT_TO_MS    = 1000;
const uint8_t  MOD_PERIOD_MS      = 50;     // duty<100 일 때 켜고 끄는 주기 (떨림 질감)
const uint8_t  KA_HALF_MS         = 5;      // 유지 신호 토글 간격 (상승 에지 10ms마다)
const uint8_t  SENSOR_HZ          = 100;

enum Sys : uint8_t { SYS_IDLE = 0, SYS_ARMED = 1, SYS_FAULT = 9 };
enum Mode : uint8_t { M_OFF = 0, M_PULSE = 1, M_HOLD = 2, M_REST = 3 };

struct Chan {
  uint8_t gate, trig, ka;
  uint8_t mode;
  uint32_t t0, lastRefresh, lastEnd, restUntil, lastKa, lastErr;
  uint16_t dur; uint8_t duty, env;
  bool kaLevel;
  uint16_t holdSlot[HOLD_SLOTS]; uint32_t holdSlotIdx;       // 무게 누적 (10초 칸별 ms)
};
Chan ch[2] = {
  {PIN_GATE1, 17, 32},
  {PIN_GATE2, 19, 33},
};

volatile uint8_t sys = SYS_IDLE;
volatile bool estopFlag = false;
uint32_t lastHeartbeat = 0;

const uint8_t LOG_N = MAX_TRIG_PER_MIN + 8;    // 반동 기록 (두 채널 합산). 분당 제한보다 커야 제한이 동작한다
uint32_t logT[LOG_N]; uint16_t logD[LOG_N]; uint8_t logI = 0;

float roll = 0, pitch = 0;
uint32_t lastSensor = 0; uint16_t seq = 0;
char rx[64]; uint8_t rxLen = 0;

// ---------- 유틸 ----------
void sendLine(const char* body) {
  uint8_t cs = 0; for (const char* p = body; *p; p++) cs ^= *p;
  Serial.print('$'); Serial.print(body); Serial.print('*');
  if (cs < 16) Serial.print('0'); Serial.println(cs, HEX);
}
void sendf(const char* fmt, int a1, int a2 = 0, int a3 = 0) {
  char b[40]; snprintf(b, sizeof b, fmt, a1, a2, a3); sendLine(b);
}

void chanOff(Chan& c) {
  digitalWrite(c.gate, LOW);
  digitalWrite(c.ka, LOW); c.kaLevel = false;
}
void holdStop(Chan& c, uint32_t now, bool rest);
// 어떤 경로로 끊겨도($X, 하트비트, ARM, 비상정지) 무게 사용 시간을 기록해야 예산을 우회할 수 없다
void allOff() {
  uint32_t now = millis();
  for (uint8_t i = 0; i < 2; i++) {
    Chan& c = ch[i];
    if (c.mode == M_HOLD) { holdStop(c, now, false); continue; }
    chanOff(c);
    if (c.mode == M_PULSE) { c.lastEnd = now; c.mode = M_OFF; }
  }
}
// 인터럽트 안전 차단: 레지스터 직접 쓰기 (IRAM에서 실행)
void IRAM_ATTR estopISR() {
  REG_WRITE(GPIO_OUT_W1TC_REG, (1UL << PIN_GATE1) | (1UL << PIN_GATE2));
  estopFlag = true;
}

void enterFault(uint8_t code) {
  allOff(); sys = SYS_FAULT;
  sendf("E,%d,FAULT", code);
  tone(PIN_BUZZ, 2000, 800);
}

bool anyActive() { return ch[0].mode == M_PULSE || ch[0].mode == M_HOLD || ch[1].mode == M_PULSE || ch[1].mode == M_HOLD; }

void chanStart(Chan& c) {
  digitalWrite(c.trig, LOW); delayMicroseconds(100); digitalWrite(c.trig, HIGH);  // 555 켜기
  c.kaLevel = true; digitalWrite(c.ka, HIGH); c.lastKa = millis();                // 첫 유지 에지
  digitalWrite(c.gate, HIGH);
}

// ---------- 예산 ----------
bool pulseBudgetOK(uint32_t now, uint16_t dur) {
  uint32_t on = 0; uint8_t cnt = 0;
  for (uint8_t i = 0; i < LOG_N; i++) {
    if (!logT[i]) continue;
    if (now - logT[i] < PULSE_WINDOW_MS) on += logD[i];
    if (now - logT[i] < 60000UL) cnt++;
  }
  return (on + dur <= MAX_PULSE_ON_WIN) && (cnt < MAX_TRIG_PER_MIN);
}
// 지금 칸으로 넘어가면서 지나간 칸을 비운다
void holdAdvance(Chan& c, uint32_t now) {
  uint32_t idx = now / HOLD_SLOT_MS;
  uint32_t d = idx - c.holdSlotIdx;
  if (!d) return;
  if (d >= HOLD_SLOTS) memset(c.holdSlot, 0, sizeof c.holdSlot);
  else for (uint32_t k = 1; k <= d; k++) c.holdSlot[(c.holdSlotIdx + k) % HOLD_SLOTS] = 0;
  c.holdSlotIdx = idx;
}
uint32_t holdUsed(Chan& c, uint32_t now) {
  holdAdvance(c, now);
  uint32_t s = 0;
  for (uint8_t i = 0; i < HOLD_SLOTS; i++) s += c.holdSlot[i];
  return s;
}
void holdStop(Chan& c, uint32_t now, bool rest) {
  chanOff(c);
  uint32_t len = now - c.t0;
  holdAdvance(c, now);
  uint16_t& slot = c.holdSlot[c.holdSlotIdx % HOLD_SLOTS];
  slot = (slot + len > 65000UL) ? 65000 : slot + len;
  c.lastEnd = now;
  if (rest) { c.mode = M_REST; c.restUntil = now + HOLD_REST_MS; }
  else c.mode = M_OFF;
}

// ---------- 명령 ----------
void cmdPulse(int n, int dur, int duty, int env) {
  uint32_t now = millis();
  if (sys != SYS_ARMED) { sendLine("E,4,NOT_ARMED"); return; }
  if (n != 1 && n != 2) { sendLine("E,10,BAD_CH"); return; }
  Chan& c = ch[n - 1];
  if (c.mode != M_OFF) { sendLine("E,12,BUSY"); return; }
  if (now - c.lastEnd < MIN_GAP_MS) { sendLine("E,14,TOO_SOON"); return; }
  dur = constrain(dur, 10, MAX_PULSE_MS); duty = constrain(duty, 10, 100);
  if (!pulseBudgetOK(now, dur)) { sendLine("E,5,BUDGET"); return; }
  logT[logI] = now ? now : 1; logD[logI] = dur; logI = (logI + 1) % LOG_N;
  c.dur = dur; c.duty = duty; c.env = env; c.t0 = now; c.mode = M_PULSE;
  chanStart(c);
  sendf("K,T,%d,%d,%d", n, dur, duty);
}

void cmdHold(int mask) {
  uint32_t now = millis();
  if (sys != SYS_ARMED) {
    if (mask) { static uint32_t le = 0; if (now - le > 500) { sendLine("E,4,NOT_ARMED"); le = now; } }
    return;
  }
  for (uint8_t i = 0; i < 2; i++) {
    Chan& c = ch[i];
    bool want = mask & (1 << i);
    if (want) {
      if (c.mode == M_HOLD) { c.lastRefresh = now; continue; }
      if (c.mode == M_PULSE) continue;                     // 반동 끝나면 다음 재전송에서 시작
      if (c.mode == M_REST) {
        if (now - c.lastErr > 500) { sendf("E,11,HOLD_REST,%d", i + 1); c.lastErr = now; }
        continue;
      }
      if (now - c.lastEnd < HOLD_MIN_GAP_MS) continue;     // 다음 재전송에서 다시 시도
      if (holdUsed(c, now) >= MAX_HOLD_IN_WIN) {
        if (now - c.lastErr > 500) { sendf("E,13,HOLD_BUDGET,%d", i + 1); c.lastErr = now; }
        continue;
      }
      c.t0 = now; c.lastRefresh = now; c.mode = M_HOLD;
      chanStart(c);
      sendf("K,W,%d,1", i + 1);
    } else if (c.mode == M_HOLD) {
      holdStop(c, now, false);
      sendf("K,W,%d,0", i + 1);
    }
  }
}

// ---------- 시리얼 ----------
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
    case 'X': allOff(); if (sys != SYS_FAULT) sys = SYS_IDLE; sendLine("K,X"); break;
    case 'A': {
      int v = atoi(body + 2);
      if (v == 1) {
        if (sys == SYS_FAULT)                  sendLine("E,7,IN_FAULT");
        else if (digitalRead(PIN_ARM) == HIGH) sendLine("E,2,ARM_SWITCH_OFF");
        else { sys = SYS_ARMED; sendLine("K,A,1"); }
      } else { allOff(); if (sys != SYS_FAULT) sys = SYS_IDLE; sendLine("K,A,0"); }
    } break;
    case 'T': {
      int n = 1, dur = 0, duty = 100, env = 0;
      sscanf(body, "T,%d,%d,%d,%d", &n, &dur, &duty, &env);
      cmdPulse(n, dur, duty, env);
    } break;
    case 'W': {
      int mask = 0; sscanf(body, "W,%d", &mask);
      cmdHold(mask & 3);
    } break;
    case 'R':
      if (sys == SYS_FAULT && digitalRead(PIN_ESTOP) == HIGH) { estopFlag = false; sys = SYS_IDLE; sendLine("K,R"); }
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

// ---------- MPU-6050 ----------
void mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(0x68); Wire.write(reg); Wire.write(val); Wire.endTransmission();
}
void mpuInit() {
  mpuWrite(0x6B, 0x00); mpuWrite(0x1C, 0x10); mpuWrite(0x1B, 0x10); mpuWrite(0x1A, 0x03);
}
void sensorTick() {
  static uint32_t tPrev = micros();
  static int16_t ax = 0, ay = 0, az = 4096, gx = 0, gy = 0, gz = 0;   // 읽기 실패 시 직전 값 유지
  Wire.beginTransmission(0x68); Wire.write(0x3B);
  // EMS 노이즈로 I2C가 잠기면 Wire 타임아웃(setup 참고)이 풀어 준다. 실패하면 이번 샘플만 건너뛴다
  if (Wire.endTransmission(false) == 0 && Wire.requestFrom(0x68, 14, true) == 14) {
    ax = Wire.read() << 8 | Wire.read(); ay = Wire.read() << 8 | Wire.read(); az = Wire.read() << 8 | Wire.read();
    Wire.read(); Wire.read();
    gx = Wire.read() << 8 | Wire.read(); gy = Wire.read() << 8 | Wire.read(); gz = Wire.read() << 8 | Wire.read();
  }
  uint32_t tNow = micros(); float dt = (tNow - tPrev) * 1e-6f; tPrev = tNow;
  float axg = ax / 4096.0f, ayg = ay / 4096.0f, azg = az / 4096.0f;
  float gxd = gx / 32.8f, gyd = gy / 32.8f, gzd = gz / 32.8f;
  roll  = 0.98f * (roll  + gxd * dt) + 0.02f * atan2(ayg, azg) * 57.2958f;
  pitch = 0.98f * (pitch + gyd * dt) + 0.02f * atan2(-axg, sqrt(ayg * ayg + azg * azg)) * 57.2958f;
  uint8_t st = (sys == SYS_FAULT) ? 9 : (anyActive() ? 2 : sys);
  char b[96], r[8], p[8];
  dtostrf(roll, 1, 1, r); dtostrf(pitch, 1, 1, p);
  snprintf(b, sizeof b, "S,%u,%s,%s,%d,%d,%d,%d,%d,%d,%d,%u",
           seq++, r, p, (int)gxd, (int)gyd, (int)gzd,
           (int)(axg * 100), (int)(ayg * 100), (int)(azg * 100), -1, st);
  sendLine(b);
}

// ---------- setup / loop ----------
void setup() {
  for (uint8_t i = 0; i < 2; i++) {
    pinMode(ch[i].gate, OUTPUT); digitalWrite(ch[i].gate, LOW);   // 가장 먼저 OFF
    pinMode(ch[i].ka, OUTPUT);   digitalWrite(ch[i].ka, LOW);
    pinMode(ch[i].trig, OUTPUT); digitalWrite(ch[i].trig, HIGH);
  }
  pinMode(PIN_ESTOP, INPUT_PULLUP); pinMode(PIN_ARM, INPUT_PULLUP);
  pinMode(PIN_BUZZ, OUTPUT); pinMode(PIN_LED, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_ESTOP), estopISR, FALLING);
  Serial.begin(115200);
  Wire.begin(PIN_SDA, PIN_SCL, 400000);
  Wire.setTimeOut(3);   // ms. I2C가 잠겨도 루프가 워치독 시간 안에 돈다
  mpuInit();
  // 태스크 워치독: loop가 250ms 안에 돌지 않으면 패닉 리셋 -> 핀 Hi-Z -> 외부 풀다운으로 OFF
  esp_task_wdt_config_t cfg = { .timeout_ms = WDT_TIMEOUT_MS, .idle_core_mask = 0, .trigger_panic = true };
  if (esp_task_wdt_reconfigure(&cfg) != ESP_OK) esp_task_wdt_init(&cfg);
  esp_task_wdt_add(NULL);
  sendLine("I,EMS_RECOIL,esp32-v2.1,PULSE<=250,HOLD<=5000");
}

void loop() {
  esp_task_wdt_reset();
  readSerial();
  // 명령 처리 뒤에 시각을 읽는다. 앞에서 읽으면 명령이 기록한 시각이 now보다 커져
  // (now - t) 부호 없는 뺄셈이 뒤집히고, 자극이 즉시 끝나거나 하트비트 끊김으로 오판한다.
  uint32_t now = millis();

  // --- 시스템 안전 감시 ---
  if ((estopFlag || digitalRead(PIN_ESTOP) == LOW) && sys != SYS_FAULT) enterFault(1);
  if (sys != SYS_FAULT && sys != SYS_IDLE && digitalRead(PIN_ARM) == HIGH) {
    allOff(); sys = SYS_IDLE; sendLine("E,2,ARM_SWITCH_OFF");
  }
  if (sys == SYS_ARMED && now - lastHeartbeat > HEARTBEAT_TO_MS) {
    allOff(); sys = SYS_IDLE; sendLine("E,3,HEARTBEAT_LOST");
  }

  // --- 채널별 상태 ---
  for (uint8_t i = 0; i < 2; i++) {
    Chan& c = ch[i];
    if (c.mode == M_PULSE) {
      uint32_t el = now - c.t0;
      if (el >= c.dur) { chanOff(c); c.lastEnd = now; c.mode = M_OFF; }
      else {
        uint8_t d = c.duty;
        if (c.env == 1) d = 100 - (uint32_t)(100 - c.duty) * el / c.dur;
        bool on = (d >= 100) || ((el % MOD_PERIOD_MS) < (uint32_t)MOD_PERIOD_MS * d / 100);
        digitalWrite(c.gate, on ? HIGH : LOW);
      }
    } else if (c.mode == M_HOLD) {
      if (now - c.lastRefresh > HOLD_REFRESH_TO_MS) { holdStop(c, now, false); sendf("K,W,%d,0", i + 1); }
      else if (now - c.t0 >= MAX_HOLD_MS) { holdStop(c, now, true); sendf("E,11,HOLD_LIMIT,%d", i + 1); }
      else if (holdUsed(c, now) + (now - c.t0) >= MAX_HOLD_IN_WIN) { holdStop(c, now, true); sendf("E,13,HOLD_BUDGET,%d", i + 1); }
    } else if (c.mode == M_REST && (int32_t)(now - c.restUntil) >= 0) {
      c.mode = M_OFF;
    }
    // 유지 신호: 자극 중에만 토글 (루프가 멈추면 555가 0.05초 안에 차단)
    if ((c.mode == M_PULSE || c.mode == M_HOLD) && now - c.lastKa >= KA_HALF_MS) {
      c.kaLevel = !c.kaLevel; digitalWrite(c.ka, c.kaLevel); c.lastKa = now;
    }
  }

  if (now - lastSensor >= 1000 / SENSOR_HZ) { lastSensor = now; sensorTick(); }
  digitalWrite(PIN_LED, sys == SYS_ARMED ? HIGH : LOW);
}
