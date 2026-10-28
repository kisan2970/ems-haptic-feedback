// 펌웨어 안전 예산 PC 시뮬레이션 (하드웨어 없이 실행)
// 아두이노 API를 흉내 내고 펌웨어 .ino를 그대로 포함해 1ms 단위로 loop()를 돌린다.
//
//   우노 :  g++ -std=c++17 -w -I tools/firmware_sim/stubs -o fwsim tools/firmware_sim/sim.cpp
//   ESP32:  g++ -std=c++17 -w -DSIM_ESP32 -I tools/firmware_sim/stubs -o fwsim tools/firmware_sim/sim.cpp
//   실행 :  ./fwsim   (실패 개수가 종료 코드. 0이면 통과)
//
// Windows는 MSYS2/MinGW의 g++로 같은 명령을 쓴다.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <deque>
#include <vector>

static uint32_t g_ms = 0;
uint32_t millis() { return g_ms; }
uint32_t micros() { return g_ms * 1000; }
void delayMicroseconds(unsigned) {}
#define HEX 16
#define HIGH 1
#define LOW 0
#define OUTPUT 1
#define INPUT_PULLUP 2
#define FALLING 2
static int pinv[32];
void pinMode(int p, int m) { if (m == INPUT_PULLUP) pinv[p] = HIGH; }
void digitalWrite(int p, int v) { pinv[p] = v; }
int digitalRead(int p) { return pinv[p]; }
int digitalPinToInterrupt(int p) { return p; }
void attachInterrupt(int, void (*)(), int) {}
void tone(int, int, int) {}
#define constrain(x,a,b) ((x)<(a)?(a):((x)>(b)?(b):(x)))
char* dtostrf(double v, int, int p, char* b) { sprintf(b, "%.*f", p, v); return b; }
#define WDTO_250MS 0
void wdt_enable(int) {}
void wdt_reset() {}

std::vector<std::string> out; std::string cur;
struct SerialT {
  std::deque<char> in;
  void begin(long) {}
  int available() { return in.size(); }
  int read() { char c = in.front(); in.pop_front(); return c; }
  void print(char c) { cur += c; }
  void print(const char* s) { cur += s; }
  void print(int v, int base = 10) { char b[16]; sprintf(b, base == 16 ? "%X" : "%d", v); cur += b; }
  void println(int v, int base) { print(v, base); out.push_back(cur); cur.clear(); }
} Serial;
struct WireT {
  void begin() {} void begin(int, int, long) {} void setClock(long) {} void setWireTimeout(int, bool) {} void setTimeOut(int) {}
  void beginTransmission(int) {} void write(int) {}
  int endTransmission(bool = true) { return 0; }
  int n = 0; int requestFrom(int, int k, bool) { n = 0; return k; }
  int read() { return (n++ == 4) ? 0x10 : 0; }
} Wire;

#ifdef SIM_ESP32
#define IRAM_ATTR
#define GPIO_OUT_W1TC_REG 0
#define REG_WRITE(r, m) do { for (int _b = 0; _b < 32; _b++) if ((m) >> _b & 1) pinv[_b] = 0; } while (0)
struct esp_task_wdt_config_t { uint32_t timeout_ms; uint32_t idle_core_mask; bool trigger_panic; };
#define ESP_OK 0
int esp_task_wdt_reconfigure(esp_task_wdt_config_t*) { return 0; }
int esp_task_wdt_init(esp_task_wdt_config_t*) { return 0; }
int esp_task_wdt_add(void*) { return 0; }
int esp_task_wdt_reset() { return 0; }
#include "../../firmware/ems_recoil_esp32/ems_recoil_esp32.ino"
#else
#include "../../firmware/ems_recoil/ems_recoil.ino"
#endif

void sendCmd(const char* body) {
  uint8_t cs = 0; for (const char* p = body; *p; p++) cs ^= *p;
  char b[80]; snprintf(b, sizeof b, "$%s*%02X\n", body, cs);
  for (char* p = b; *p; p++) Serial.in.push_back(*p);
}
// run for ms; hb every 200ms; hold mask resent every 100ms if >=0; count stimulated ms per channel
long stimMs[2];
void run(uint32_t ms, int holdMask = -1) {
  for (uint32_t i = 0; i < ms; i++) {
    if (g_ms % 200 == 0) sendCmd("H");
    if (holdMask >= 0 && g_ms % 100 == 0) { char b[8]; sprintf(b, "W,%d", holdMask); sendCmd(b); }
    loop();
    for (int c = 0; c < 2; c++) if (pinv[ch[c].gate]) stimMs[c]++;
    g_ms++;
  }
}
void jump(){ sendCmd("W,0"); run(300, 0); g_ms += 120000; sendCmd("H"); sendCmd("A,1"); }
int countOut(const char* pre) { int n = 0; for (auto& s : out) if (s.find(pre) == 1) n++; return n; }

int main() {
  g_ms = 1000; pinv[PIN_ARM] = LOW; setup(); pinv[PIN_ARM] = LOW;
  sendCmd("A,1"); run(10);
  int fails = 0;
  auto expect = [&](bool ok, const char* name, long v) { printf("[%s] %s (%ld)\n", ok ? "OK" : "NG", name, v); if (!ok) fails++; };

  // 1. Short holds repeated: 1s on, 0.6s off, for 120s -> stim must be <= ~30s per 60s
  stimMs[0] = 0;
  for (int k = 0; k < 75; k++) { run(1000, 1); sendCmd("W,0"); run(600, 0); }
  expect(stimMs[0] <= 2 * 30000 + 1000, "1s 반복 들기 120초 동안 누적 <= 60초(1분 30초 예산)", stimMs[0]);
  expect(stimMs[0] >= 40000, "  예산 안에서는 정상 동작", stimMs[0]);

  // 2. X during hold then re-arm repeatedly -> still budgeted
  jump(); run(10); stimMs[0] = 0;
  for (int k = 0; k < 40; k++) { run(4000, 1); sendCmd("X"); run(10); sendCmd("A,1"); run(600); }
  expect(stimMs[0] <= 184 * 500 + 6000, "들기 중 $X 후 재아밍 반복 184초: 누적 <= 92초+한 칸", stimMs[0]);
  expect(stimMs[0] < 150000, "  (예산이 없으면 약 160초)", stimMs[0]);

  // 3. Pulse per-minute limit reachable: alternate channels, 60ms pulses every 350ms for 60s
  jump(); run(10); out.clear();
  int acc = 0;
  for (int k = 0; k < 170; k++) { char b[32]; sprintf(b, "T,%d,60,100,0", k % 2 + 1); sendCmd(b); run(350); }
  acc = countOut("K,T");
  expect(acc <= MAX_TRIG_PER_MIN + 1 && acc >= MAX_TRIG_PER_MIN - 2, "분당 반동 횟수 제한 동작 (60초 동안 ACK 수)", acc);

  // 4. Hold min gap: release then immediate re-hold
  jump(); run(10); out.clear();
  run(1000, 1); sendCmd("W,0"); run(1); run(300, 1);
  int starts = countOut("K,W,1,1");
  expect(starts == 1, "내려놓은 직후 0.3초 안에는 다시 켜지지 않음", starts);
  run(400, 1);
  expect(countOut("K,W,1,1") == 2, "0.5초 뒤에는 다시 켜짐", countOut("K,W,1,1"));

  // 5. Single hold max 5s then rest
  jump(); run(10); out.clear(); stimMs[0] = 0; sendCmd("W,0"); run(600, 0);
  run(8000, 1);
  expect(stimMs[0] >= 4900 && stimMs[0] <= 5100 + 3000, "5초 최대 후 휴식", stimMs[0]);

  // 6. Pulse duration accuracy
  jump(); run(10); stimMs[0] = 0; sendCmd("W,0"); run(600, 0); sendCmd("T,1,120,100,0"); run(500);
  expect(stimMs[0] >= 118 && stimMs[0] <= 122, "120ms 반동 길이", stimMs[0]);

  printf("fails=%d\n", fails);
  return fails;
}
