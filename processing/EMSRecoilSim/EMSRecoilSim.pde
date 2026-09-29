// EMSRecoilSim.pde  v2  -  Processing 4
// EMS 근자극 기반 반동 + 무게감 시연
//   [1] 총 모드  : 클릭 또는 F -> 반동 (CH1 손목 신전근 짧게)
//   [2] 들기 모드: P로 물체 들기/내려놓기, Z/X/C 무게 선택 -> 들고 있는 동안 계속 자극
//   [3] 벽 모드  : IMU로 손을 뻗어 벽에 부딪히면 반동
// 공통: A 아밍, SPACE 전부 정지, R FAULT 해제, T 테스트 반동 100ms
import processing.serial.*;

Serial port;
final String PORT_NAME = "COM11";        // 우노 포트. 바뀌면 콘솔의 목록 보고 수정

// ---- 반동 파라미터 ----
final int   RECOIL_MS   = 120;           // 총 반동 길이
final int   RECOIL_CH   = 1;             // 손목 신전근
// ---- 벽 매핑 ----
final float V_MAX = 3.0, GAMMA = 0.7, LEAD_S = 0.05, WALL_X = 0.72;
final int   T_MIN = 60, T_MAX = 220, REFRACT_MS = 300;
// ---- 들기 ----
// 무게 단계: {EMS 채널 마스크, 시각 추종 계수(작을수록 손이 늦게 따라옴 = 무겁게 보임)}
final String[] W_NAME = { "가벼움", "보통", "무거움" };
final int[]    W_MASK = { 0, 1, 3 };      // 0 = 자극 없음, 1 = CH1, 3 = CH1 + CH2(삼두근)
final float[]  W_FOLLOW = { 0.45, 0.18, 0.07 };
final float PITCH_MIN = -50, PITCH_MAX = 50;

int mode = 1;                // 1 총, 2 들기, 3 벽
int weight = 1;
boolean holding = false;
int lastHold = 0, lastHb = 0, lastTrig = 0;

float pitch, roll; int devState = 0;
float handX = 0.5, handV = 0, prevX = 0.5; int prevT = 0;
float liftY = 0;             // 들기 모드에서 화면 속 손 높이 (0~1)
boolean inside = false;
int flashUntil = 0; float kick = 0;
String lastMsg = "";

void setup() {
  size(1000, 600);
  frameRate(60);
  textFont(createFont("Malgun Gothic", 16));
  printArray(Serial.list());
  port = new Serial(this, PORT_NAME, 115200);
  port.bufferUntil('\n');
}

void draw() {
  int now = millis();
  if (now - lastHb > 200) { send("H"); lastHb = now; }
  // 들고 있는 동안 100ms마다 유지 신호
  if (mode == 2 && holding && now - lastHold > 100) {
    send("W," + W_MASK[weight]); lastHold = now;
  }
  background(22);
  if (mode == 1) drawGun();
  else if (mode == 2) drawLift();
  else drawWall();
  drawHud();
}

// ================= 총 모드 =================
void drawGun() {
  float aimY = map(constrain(pitch, PITCH_MIN, PITCH_MAX), PITCH_MIN, PITCH_MAX, height * 0.8, height * 0.2);
  kick *= 0.85;
  if (millis() < flashUntil) { background(90, 60, 20); }
  // 표적
  noFill(); stroke(200, 60, 60); strokeWeight(3);
  for (int r = 30; r <= 120; r += 30) ellipse(width * 0.7, height * 0.5, r * 2, r * 2);
  // 조준선
  stroke(80, 220, 120); strokeWeight(2);
  float cy = aimY - kick * 60;
  line(width * 0.7 - 20, cy, width * 0.7 + 20, cy); line(width * 0.7, cy - 20, width * 0.7, cy + 20);
  // 총
  pushMatrix(); translate(180, height * 0.62); rotate(-kick * 0.35);
  noStroke(); fill(170); rect(0, -18, 200, 30, 6); fill(120); rect(10, 10, 40, 70, 6);
  if (millis() < flashUntil) { fill(255, 220, 90); ellipse(215, -3, 50, 34); }
  popMatrix();
  fill(255); textSize(18); text("클릭 또는 F = 발사", 40, height - 60);
}
void fireGun() {
  if (millis() - lastTrig < 300) return;
  send("T," + RECOIL_CH + "," + RECOIL_MS + ",100,0");
  lastTrig = millis(); flashUntil = millis() + 80; kick = 1;
}

// ================= 들기 모드 =================
void drawLift() {
  // 실제 팔 각도 -> 목표 높이. 무거울수록 화면 속 손이 느리게 따라옴 (pseudo-haptics)
  float target = constrain(map(pitch, PITCH_MIN, PITCH_MAX, 0, 1), 0, 1);
  float follow = holding ? W_FOLLOW[weight] : 0.45;
  liftY = lerp(liftY, target, follow);
  float y = map(liftY, 0, 1, height * 0.8, height * 0.2);
  // 선반
  stroke(90); strokeWeight(4); line(560, height * 0.8 + 45, 900, height * 0.8 + 45);
  noStroke();
  // 손
  fill(240, 200, 170); ellipse(600, y + 30, 90, 36);
  // 물체
  float s = 40 + weight * 18;
  fill(holding ? color(90, 160, 240) : color(120));
  if (holding) rect(600 - s / 2, y - s + 12, s, s, 6);
  else rect(760 - s / 2, height * 0.8 + 45 - s, s, s, 6);
  fill(255); textSize(20);
  text("무게: " + W_NAME[weight] + (W_MASK[weight] == 0 ? " (자극 없음)" : W_MASK[weight] == 1 ? " (손목)" : " (손목 + 삼두근)"), 40, 110);
  textSize(18);
  text(holding ? "들고 있음 - P로 내려놓기" : "P = 들기   Z/X/C = 무게 선택", 40, height - 60);
}
void toggleHold() {
  holding = !holding;
  if (!holding) send("W,0");
  lastHold = 0;
}

// ================= 벽 모드 =================
void drawWall() {
  float wx = WALL_X * width;
  noStroke(); fill(inside ? color(220, 60, 60) : color(90)); rect(wx, 0, width - wx, height);
  fill(80, 200, 255); ellipse(handX * width, height / 2, 44, 44);
  fill(255); textSize(18); text("IMU로 손을 뻗어 벽에 부딪히기", 40, height - 60);
}
void updateWall() {
  int t = millis(); float dt = (prevT == 0) ? 0.01 : (t - prevT) / 1000.0; prevT = t;
  float x = constrain(map(pitch, PITCH_MIN, PITCH_MAX, 0, 1), 0, 1);
  handX = lerp(handX, x, 0.5);
  handV = (handX - prevX) / max(dt, 1e-3); prevX = handX;
  float depth = handX - WALL_X;
  boolean predicted = (handV > 0.2) && (depth < 0) && ((-depth) / handV < LEAD_S);
  if (!inside && (depth >= 0 || predicted)) {
    inside = true;
    if (t - lastTrig > REFRACT_MS) {
      float vn = constrain(handV / V_MAX, 0, 1);
      int dur = round(T_MIN + (T_MAX - T_MIN) * pow(vn, GAMMA));
      send("T,1," + dur + ",100,0"); lastTrig = t;
    }
  } else if (inside && depth < -0.03) inside = false;
}

// ================= 공통 =================
void drawHud() {
  fill(255); textSize(22);
  String[] names = { "", "[1] 총 반동", "[2] 물체 무게", "[3] 벽 충돌" };
  text(names[mode], 40, 50);
  textSize(14); fill(200);
  String st = devState == 9 ? "FAULT" : devState == 2 ? "자극 중" : devState == 1 ? "ARMED" : "IDLE";
  text("장치: " + st + "    pitch " + nf(pitch, 1, 1) + "    마지막 응답: " + lastMsg, 40, 76);
  text("A 아밍  SPACE 정지  R 해제  T 테스트  1/2/3 모드", 40, height - 25);
  if (devState == 2) { fill(255, 80, 80); ellipse(width - 40, 40, 24, 24); }
}

void serialEvent(Serial p) {
  String line = p.readStringUntil('\n'); if (line == null) return;
  String body = verify(line.trim()); if (body == null) return;
  String[] f = split(body, ',');
  if (f[0].equals("S") && f.length >= 12) {
    roll = float(f[2]); pitch = float(f[3]); devState = int(f[11]);
    if (mode == 3) updateWall();
  } else {
    lastMsg = body;
    if (body.startsWith("E,11") || body.startsWith("E,13")) holding = false;   // 최대 시간 도달 -> 자동 내려놓기
  }
}

void mousePressed() { if (mode == 1) fireGun(); }

void keyPressed() {
  if (key == 'a' || key == 'A') send("A,1");
  else if (key == ' ') { holding = false; send("X"); }
  else if (key == 'r' || key == 'R') send("R");
  else if (key == 't' || key == 'T') send("T,1,100,100,0");
  else if (key == 'f' || key == 'F') { if (mode == 1) fireGun(); }
  else if (key == 'p' || key == 'P') { if (mode == 2) toggleHold(); }
  else if (key == 'z' || key == 'Z') weight = 0;
  else if (key == 'x' || key == 'X') weight = 1;
  else if (key == 'c' || key == 'C') weight = 2;
  else if (key >= '1' && key <= '3') {
    if (holding) { holding = false; send("W,0"); }
    mode = key - '0';
  }
}

void exit() { send("X"); super.exit(); }

// ---- $BODY*HH ----
synchronized void send(String body) { port.write("$" + body + "*" + hex(xor(body), 2) + "\n"); }
int xor(String s) { int c = 0; for (int i = 0; i < s.length(); i++) c ^= s.charAt(i); return c & 0xFF; }
String verify(String line) {
  int a = line.indexOf('$'), b = line.lastIndexOf('*');
  if (a < 0 || b < 0 || b < a || b + 3 > line.length()) return null;
  String body = line.substring(a + 1, b);
  return (xor(body) == unhex(line.substring(b + 1, b + 3))) ? body : null;
}
