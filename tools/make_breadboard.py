"""830홀 브레드보드 실물 배치도 + 꽂는 위치 목록 생성.
출력: docs/breadboard_830.svg, docs/BREADBOARD.md  (PNG는 Edge headless로 렌더)
"""
import io, os, math, sys

SIMPLE = "--simple" in sys.argv   # 키스위치·부저·실험자 E-STOP 생략판
SUF = "_simple" if SIMPLE else ""

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, '..', 'docs')

W, H = 2000, 1260
P = 22
X0 = 520
ROW = {'a': 400, 'b': 422, 'c': 444, 'd': 466, 'e': 488, 'f': 532, 'g': 554, 'h': 576, 'i': 598, 'j': 620}
RAIL = {'T+': 330, 'T-': 352, 'B-': 668, 'B+': 690}
RAILCOLS = [c for c in range(2, 61) if (c - 1) % 6 != 0]
F = 'font-family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"'

o = []        # svg body
wires = []    # drawn last
steps = []    # netlist lines for markdown
used = set()

def a(s): o.append(s)
def cx(c): return X0 + (c - 1) * P
def hole(spec):
    if spec[0] in 'TB':
        r, c = spec[:2], int(spec[2:])
        assert c in RAILCOLS, 'no rail hole ' + spec
        return (cx(c), RAIL[r])
    return (cx(int(spec[1:])), ROW[spec[0]])
def use(spec):
    assert spec not in used, 'duplicate hole ' + spec
    used.add(spec)
    return hole(spec)
def nice(spec):
    if spec[0] in 'TB':
        nm = {'T+': '위 + 레일', 'T-': '위 − 레일', 'B-': '아래 − 레일', 'B+': '아래 + 레일'}[spec[:2]]
        return f'{nm} {spec[2:]}열'
    return f'{spec[0]}{spec[1:]}'
def text(x, y, t, size=13, anchor='middle', c='#222', bold=False, extra=''):
    b = 'font-weight="700"' if bold else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {b} {extra}>{t}</text>')
def wtext(x, y, t, size=13, anchor='middle', c='#222', bold=False):
    b = 'font-weight="700"' if bold else ''
    wires.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {b}>{t}</text>')

BAND = {'violet': '#7d3cc8', 'green': '#2e9e4f', 'black': '#111', 'brown': '#7b4a1e', 'red': '#d0261f', 'orange': '#f08a24', 'yellow': '#f2cf2b', 'gold': '#c9a227'}
RES = {
    '330Ω': ['orange', 'orange', 'black', 'black', 'brown'],
    '1kΩ': ['brown', 'black', 'black', 'brown', 'brown'],
    '10kΩ': ['brown', 'black', 'black', 'red', 'brown'],
    '100kΩ': ['brown', 'black', 'black', 'orange', 'brown'],
    '1MΩ': ['brown', 'black', 'black', 'yellow', 'brown'],
    '500kΩ': ['green', 'black', 'black', 'orange', 'brown'],
    '470kΩ': ['yellow', 'violet', 'black', 'orange', 'brown'],
}

def pin_end(x, y):
    return f'<rect x="{x-3.5}" y="{y-3.5}" width="7" height="7" rx="1.5" fill="#c9c9c9" stroke="#666" stroke-width="1"/>'

def resistor(h1, h2, val, ch, lab_off=(0, -13)):
    (x1, y1), (x2, y2) = use(h1), use(h2)
    L = math.hypot(x2 - x1, y2 - y1); ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    bl = min(30, L - 10)
    s = [f'<g transform="translate({mx},{my}) rotate({ang})">',
         f'<line x1="{-L/2}" y1="0" x2="{L/2}" y2="0" stroke="#9a9a9a" stroke-width="2.6"/>',
         f'<rect x="{-bl/2}" y="-6.5" width="{bl}" height="13" rx="6" fill="#8ec2e6" stroke="#4f7fa3" stroke-width="1.2"/>']
    pos = [-bl / 2 + 4, -bl / 2 + 8.5, -bl / 2 + 13, -bl / 2 + 17.5, bl / 2 - 5]
    for p, col in zip(pos, RES[val]):
        s.append(f'<rect x="{p}" y="-6.5" width="2.6" height="13" fill="{BAND[col]}"/>')
    s.append('</g>')
    s.append(pin_end(x1, y1)); s.append(pin_end(x2, y2))
    lx, ly = mx + lab_off[0], my + lab_off[1]
    s.append(f'<rect x="{lx-19}" y="{ly-9}" width="38" height="13" rx="3" fill="#fffbe6" stroke="#bbb" stroke-width="0.8" opacity="0.95"/>')
    s.append(f'<text x="{lx}" y="{ly+1.5}" font-size="9.5" text-anchor="middle" fill="#333" {F}>{val}</text>')
    a('\n'.join(s))
    steps.append((ch, f'저항 {val}', f'{nice(h1)} ↔ {nice(h2)}'))

def ceramic(h1, h2, code, val, ch, lab_off=(0, -14)):
    (x1, y1), (x2, y2) = use(h1), use(h2)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#9a9a9a" stroke-width="2.4"/>')
    a(f'<ellipse cx="{mx}" cy="{my}" rx="10" ry="8.5" fill="#e1a62e" stroke="#9c6d12" stroke-width="1.2"/>')
    a(f'<text x="{mx}" y="{my+3}" font-size="8" text-anchor="middle" fill="#3a2a00" {F} font-weight="700">{code}</text>')
    a(pin_end(x1, y1)); a(pin_end(x2, y2))
    lx, ly = mx + lab_off[0], my + lab_off[1]
    a(f'<text x="{lx}" y="{ly}" font-size="9.5" text-anchor="middle" fill="#333" {F}>{val}</text>')
    steps.append((ch, f'커패시터 {val} ({code})', f'{nice(h1)} ↔ {nice(h2)}'))

def jumper(h1, h2, color, ch, what):
    (x1, y1), (x2, y2) = use(h1), use(h2)
    wires.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#00000055" stroke-width="8" stroke-linecap="round"/>')
    wires.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="5.5" stroke-linecap="round"/>')
    wires.append(pin_end(x1, y1)); wires.append(pin_end(x2, y2))
    steps.append((ch, f'점퍼선 ({what})', f'{nice(h1)} ↔ {nice(h2)}'))

def flex(p1, p2, color, c1, c2, w=5.5, end2_pin=True, end1_pin=True):
    x1, y1 = p1; x2, y2 = p2
    d = f'M{x1},{y1} C{c1[0]},{c1[1]} {c2[0]},{c2[1]} {x2},{y2}'
    wires.append(f'<path d="{d}" fill="none" stroke="#00000050" stroke-width="{w+2.5}" stroke-linecap="round"/>')
    wires.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
    if end1_pin: wires.append(pin_end(x1, y1))
    if end2_pin: wires.append(pin_end(x2, y2))

def flexpath(d, color, w=5.5):
    wires.append(f'<path d="{d}" fill="none" stroke="#00000050" stroke-width="{w+2.5}" stroke-linecap="round"/>')
    wires.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')

def dip(c0, n, label, ch, names):
    for i in range(n):
        use(f'f{c0+i}'); use(f'e{c0+i}')
    xl, xr = cx(c0) - 12, cx(c0 + n - 1) + 12
    for i in range(n):
        x = cx(c0 + i)
        a(f'<rect x="{x-3}" y="480" width="6" height="10" fill="#cfcfcf"/>')
        a(f'<rect x="{x-3}" y="530" width="6" height="10" fill="#cfcfcf"/>')
    a(f'<rect x="{xl}" y="486" width="{xr-xl}" height="48" rx="3" fill="#1c1c1c" stroke="#000" stroke-width="1"/>')
    a(f'<path d="M{xl},503 a7,7 0 0 1 0,14" fill="#444"/>')
    a(f'<circle cx="{xl+7}" cy="527" r="2.6" fill="#777"/>')
    a(f'<text x="{(xl+xr)/2}" y="514" font-size="{10 if n>2 else 8.5}" text-anchor="middle" fill="#eee" {F} font-weight="700">{label}</text>')
    a(f'<text x="{(xl+xr)/2}" y="526" font-size="7.5" text-anchor="middle" fill="#aaa" {F}>{names}</text>')
    pins_b = ', '.join(f'{i+1}번=f{c0+i}' for i in range(n))
    pins_t = ', '.join(f'{2*n-i}번=e{c0+i}' for i in range(n))
    steps.append((ch, f'{label} (홈이 왼쪽)', f'{pins_b} / {pins_t}'))

def to92(cols, row, label, ch, legs):
    for c in cols: use(f'{row}{c}')
    xm = cx(cols[1])
    if row == 'e':
        yb = 507; path = f'M{xm-30},{yb} L{xm+30},{yb} Q{xm+30},{yb-30} {xm},{yb-30} Q{xm-30},{yb-30} {xm-30},{yb} Z'; ty = yb - 5
    else:
        yb = 513; path = f'M{xm-30},{yb} L{xm+30},{yb} Q{xm+30},{yb+30} {xm},{yb+30} Q{xm-30},{yb+30} {xm-30},{yb} Z'; ty = yb + 21
    a(f'<path d="{path}" fill="#151515" stroke="#000"/>')
    a(f'<line x1="{xm-30}" y1="{yb}" x2="{xm+30}" y2="{yb}" stroke="#666" stroke-width="2"/>')
    for c, L in zip(cols, legs):
        a(f'<text x="{cx(c)}" y="{ty}" font-size="9" text-anchor="middle" fill="#ffd54a" {F} font-weight="700">{L}</text>')
    a(f'<text x="{xm}" y="{ty - 10 if row=="e" else ty - 9}" font-size="7.5" text-anchor="middle" fill="#ccc" {F}>{label}</text>')
    steps.append((ch, f'트랜지스터 {label}', ', '.join(f'{L}={row}{c}' for c, L in zip(cols, legs)) + ' (평평한 면이 가운데 홈 쪽)'))

# ------------------------------------------------------------------ canvas & board
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><linearGradient id="pcb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1e74a8"/><stop offset="1" stop-color="#155a85"/></linearGradient>'
  '<filter id="sh" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-opacity="0.25"/></filter></defs>')
a(f'<rect width="{W}" height="{H}" fill="#e9e6df"/>')
text(40, 44, '브레드보드 실물 배치도 (830홀) — 아두이노 우노 · 2채널 v2' + (' · 간소화판' if SIMPLE else ''), 26, 'start', bold=True)
if SIMPLE: text(40, 96, '키스위치 · 부저 · 실험자 E-STOP 생략', 14, 'start', c='#c0392b', bold=True)
text(40, 70, '총 반동 + 물체 무게 · 위에서 내려다본 모습 · 구멍 위치는 docs/BREADBOARD' + SUF + '.md 목록과 같음', 14, 'start', c='#555')

bx0, bx1 = X0 - 42, cx(63) + 42
a(f'<rect x="{bx0}" y="305" width="{bx1-bx0}" height="410" rx="10" fill="#f6f4ee" stroke="#cfc9bb" stroke-width="2" filter="url(#sh)"/>')
a(f'<rect x="{bx0+8}" y="502" width="{bx1-bx0-16}" height="16" rx="3" fill="#dcd6c8"/>')
for y, col in [(318, '#d62728'), (364, '#2f6fd6'), (656, '#2f6fd6'), (702, '#d62728')]:
    a(f'<line x1="{bx0+20}" y1="{y}" x2="{bx1-20}" y2="{y}" stroke="{col}" stroke-width="2"/>')
for y, sgn, col in [(334, '+', '#d62728'), (356, '−', '#2f6fd6'), (672, '−', '#2f6fd6'), (694, '+', '#d62728')]:
    text(bx0 + 14, y, sgn, 15, c=col, bold=True); text(bx1 - 14, y, sgn, 15, c=col, bold=True)
def hole_svg(x, y): return f'<rect x="{x-3.6}" y="{y-3.6}" width="7.2" height="7.2" rx="1.2" fill="#3b3b3b" stroke="#9b9586" stroke-width="0.8"/>'
for c in range(1, 64):
    for r, y in ROW.items(): a(hole_svg(cx(c), y))
for c in RAILCOLS:
    for y in RAIL.values(): a(hole_svg(cx(c), y))
for c in [1] + list(range(5, 64, 5)):
    text(cx(c), 389, str(c), 9, c='#8a8473'); text(cx(c), 646, str(c), 9, c='#8a8473')
for r, y in ROW.items():
    text(bx0 + 16, y + 4, r, 10, c='#8a8473'); text(bx1 - 16, y + 4, r, 10, c='#8a8473')
text(cx(16.5), 514, 'CH1 · 손목 신전근', 10, c='#6b6455', bold=True)
text(cx(46.5), 514, 'CH2 · 삼두근', 10, c='#6b6455', bold=True)
for c0 in (20, 50):
    a(f'<rect x="{cx(c0)-11}" y="390" width="{2*P}" height="106" rx="4" fill="#ff8a3d22" stroke="#e8731a" stroke-width="1.5" stroke-dasharray="4,3"/>')
    text(cx(c0) + 11, 383, 'TENS 전용', 9.5, c='#c4560f', bold=True)

# ------------------------------------------------------------------ channels
YEL, GRN, BLU, RED, BLK = '#f2c12e', '#2e9e4f', '#2f6fd6', '#d62728', '#222'
def channel(o, ch, ka_hole):
    qk = 'Q3' if o == 0 else 'Q4'; qg = 'Q1' if o == 0 else 'Q2'
    # ---- 위쪽: 유지 신호 → Q3 → 555 타이밍
    use(ka_hole)
    steps.append((ch, f'유지 신호 선 도착점', nice(ka_hole)))
    ceramic(f'c{3+o}', f'c{5+o}', '104', '100nF', ch, lab_off=(0, -13))
    resistor(f'b{5+o}', f'b{8+o}', '1kΩ', ch, lab_off=(0, -12))
    resistor(f'a{8+o}', f'T-{9+o}', '10kΩ', ch, lab_off=(-24, -2))
    to92([7 + o, 8 + o, 9 + o], 'e', f'Q{3 if o == 0 else 4} 2N3904', ch, ['E', 'B', 'C'])
    jumper(f'a{7+o}', f'T-{6+o}', BLK, ch, f'{qk} 이미터 → GND')
    jumper(f'd{9+o}', f'd{11+o}', GRN, ch, f'{qk} 컬렉터 → 555 7번')
    dip(10 + o, 4, 'TLC555', ch, '8   7   6   5')
    jumper(f'a{10+o}', f'T+{10+o}', RED, ch, '555 8번 → 5V')
    jumper(f'b{11+o}', f'b{12+o}', GRN, ch, '555 7번 ↔ 6번')
    resistor(f'a{11+o}', f'T+{11+o}', '470kΩ', ch, lab_off=(-26, 4))
    ceramic(f'a{12+o}', f'T-{12+o}', '104', '100nF', ch, lab_off=(15, -15))
    ceramic(f'a{13+o}', f'T-{14+o}', '103', '10nF', ch, lab_off=(19, 0))
    # ---- 아래쪽: 트리거, 출력, 게이트
    use(f'j{8+o}'); steps.append((ch, '트리거 선 도착점', f'j{8+o}'))
    ceramic(f'h{8+o}', f'h{11+o}', '103', '10nF', ch, lab_off=(0, 16))
    jumper(f'j{10+o}', f'B-{10+o}', BLK, ch, '555 1번 → GND')
    resistor(f'i{11+o}', f'B+{11+o}', '10kΩ', ch, lab_off=(-23, 18))
    jumper(f'j{13+o}', f'B+{14+o}', RED, ch, '555 4번 → 5V')
    resistor(f'g{12+o}', f'g{16+o}', '330Ω', ch, lab_off=(0, -11))
    jumper(f'h{16+o}', f'h{20+o}', '#8e44ad', ch, '330Ω → PhotoMOS 1번')
    dip(20 + o, 2, 'AQY', ch, '4  3')
    to92([23 + o, 24 + o, 25 + o], 'f', f'Q{1 if o == 0 else 2} 2N3904', ch, ['C', 'B', 'E'])
    jumper(f'h{23+o}', f'h{21+o}', '#8e44ad', ch, f'{qg} 컬렉터 → PhotoMOS 2번')
    jumper(f'j{25+o}', f'B-{24+o}', BLK, ch, f'{qg} 이미터 → GND')
    resistor(f'i{24+o}', f'i{28+o}', '1kΩ', ch, lab_off=(0, 14))
    use(f'g{28+o}'); steps.append((ch, '게이트 선 도착점', f'g{28+o}'))
    resistor(f'j{28+o}', f'B-{28+o}', '10kΩ', ch, lab_off=(24, 2))
    use(f'a{20+o}'); use(f'a{21+o}')
    steps.append((ch, 'TENS 출력 (주황)', f'a{21+o} ← TENS 리드 A(잘라서), a{20+o} → 비상정지 NC → 참가자 STOP NC → 패드 A'))

channel(0, 'CH1', 'a3')
channel(30, 'CH2', 'e33')

# 레일 다리
jumper('T+60', 'B+60', RED, '공통', '위 + 레일 ↔ 아래 + 레일')
jumper('T-59', 'B-59', BLK, '공통', '위 − 레일 ↔ 아래 − 레일')

# ------------------------------------------------------------------ Arduino (90° 회전: USB 위, 디지털 헤더 오른쪽)
ax0, ay0, ax1, ay1 = 80, 290, 360, 770
a(f'<rect x="{ax0}" y="{ay0}" width="{ax1-ax0}" height="{ay1-ay0}" rx="14" fill="url(#pcb)" stroke="#0f4766" stroke-width="2" filter="url(#sh)"/>')
for hx, hy in [(100, 312), (338, 312), (100, 748), (338, 748)]:
    a(f'<circle cx="{hx}" cy="{hy}" r="7" fill="#e9e6df" stroke="#c9a227" stroke-width="2"/>')
a('<rect x="175" y="268" width="56" height="34" rx="6" fill="#c8c8c8" stroke="#888" stroke-width="1.5"/>')
text(203, 290, 'USB-C', 9, c='#444', bold=True)
a('<rect x="270" y="262" width="48" height="44" rx="4" fill="#222"/>')
a('<rect x="170" y="470" width="96" height="96" rx="4" fill="#202020" stroke="#000"/>')
text(218, 515, 'ATmega', 11, c='#ccc'); text(218, 530, '328P', 11, c='#ccc')
a('<rect x="205" y="360" width="30" height="20" rx="3" fill="#ddd"/><circle cx="220" cy="370" r="6" fill="#c33"/>')
text(220, 640, 'UNO R3', 22, c='#fff', bold=True)
text(220, 662, 'COM11', 12, c='#bfe0f5')
RIGHT = {'SCL': 330, 'SDA': 352, 'AREF': 374, 'GND ': 396, 'D13': 418, 'D12': 440, 'D11': 462, 'D10': 484, 'D9': 506, 'D8': 528,
         'D7': 560, 'D6': 582, 'D5': 604, 'D4': 626, 'D3': 648, 'D2': 670, 'D1': 692, 'D0': 714}
LEFT = {'IOREF': 422, 'RESET': 444, '3.3V': 466, '5V': 488, 'GND': 510, 'GND2': 532, 'VIN': 554,
        'A0': 590, 'A1': 612, 'A2': 634, 'A3': 656, 'A4': 678, 'A5': 700}
a('<rect x="337" y="318" width="16" height="222" rx="2" fill="#1a1a1a"/><rect x="337" y="548" width="16" height="178" rx="2" fill="#1a1a1a"/>')
a('<rect x="87" y="410" width="16" height="156" rx="2" fill="#1a1a1a"/><rect x="87" y="578" width="16" height="134" rx="2" fill="#1a1a1a"/>')
for n, y in RIGHT.items():
    a(f'<rect x="341" y="{y-4}" width="8" height="8" fill="#555"/>'); text(330, y + 4, n.strip(), 10, 'end', c='#fff', bold=True)
for n, y in LEFT.items():
    a(f'<rect x="91" y="{y-4}" width="8" height="8" fill="#555"/>'); text(110, y + 4, 'GND' if n == 'GND2' else n, 10, 'start', c='#fff', bold=True)
def RP(n): return (345, RIGHT[n])
def LP(n): return (95, LEFT[n])

# ------------------------------------------------------------------ IMU
a('<rect x="60" y="830" width="200" height="110" rx="6" fill="#5b2d8a" stroke="#3a1a5e" stroke-width="2" filter="url(#sh)"/>')
a('<rect x="135" y="875" width="34" height="34" fill="#111"/>')
text(160, 930, 'GY-521 (MPU-6050)', 11, c='#fff', bold=True)
IMU = {}
for i, n in enumerate(['VCC', 'GND', 'SCL', 'SDA', 'XDA', 'XCL', 'AD0', 'INT']):
    x = 80 + i * 23; IMU[n] = (x, 842)
    a(f'<circle cx="{x}" cy="842" r="5" fill="#d9b44a" stroke="#7a5c10"/>'); text(x, 862, n, 7.5, c='#fff')
flex(LP('3.3V'), IMU['VCC'], RED, (40, 466), (80, 790))
flex(LP('GND2'), IMU['GND'], BLK, (48, 532), (103, 800))
flex(LP('A5'), IMU['SCL'], '#7d3cc8', (55, 700), (126, 800))
flex(LP('A4'), IMU['SDA'], '#e8e8e8', (62, 678), (149, 805))
steps.append(('공통', 'IMU (GY-521)', '우노 3.3V → VCC, 우노 GND → GND, A5 → SCL, A4 → SDA. 시연 때는 긴 선으로 손등에 고정'))

# 우노 전원 → 레일
flexpath('M95,488 L54,488 Q42,488 42,476 L42,232 Q42,220 54,220 L530,220 Q542,220 542,232 L542,330', RED); wires.append(pin_end(542, 330)); used.add('T+2')
flexpath('M95,510 L42,510 Q30,510 30,498 L30,217 Q30,205 42,205 L574,205 Q586,205 586,217 L586,352', BLK); wires.append(pin_end(586, 352)); used.add('T-4')
steps.append(('공통', '전원', '우노 5V → 위 + 레일 2열, 우노 GND → 위 − 레일 4열'))

# 디지털 신호
flex(RP('D9'), hole('a3'), YEL, (430, 506), (564, 280)); wtext(372, 500, 'D9', 11, 'start', c='#7a5c00', bold=True)
flex(RP('D10'), hole('e33'), YEL, (520, 470), (1224, 860))
flex(RP('D4'), hole('j8'), GRN, (450, 800), (674, 790))
flex(RP('D7'), hole('j38'), GRN, (520, 850), (1334, 830))
flex(RP('D5'), hole('g28'), BLU, (480, 820), (1114, 810))
flex(RP('D6'), hole('g58'), BLU, (560, 880), (1774, 850))
for n, col in [('D10', '#7a5c00'), ('D7', '#1d6b35'), ('D6', '#1f4f9e'), ('D5', '#1f4f9e'), ('D4', '#1d6b35')]:
    wtext(372, RIGHT[n] - 4, n, 11, 'start', c=col, bold=True)
steps.append(('공통', '우노 신호선', 'D9 → a3, D4 → j8, D5 → g28 (CH1) / D10 → e33, D7 → j38, D6 → g58 (CH2)'))

# ------------------------------------------------------------------ 패널 부품 (아래)
if not SIMPLE:
    a('<circle cx="700" cy="960" r="36" fill="#cfd3d6" stroke="#7f878c" stroke-width="3" filter="url(#sh)"/>')
    a('<circle cx="700" cy="960" r="20" fill="#9aa3a8"/><rect x="696" y="946" width="8" height="28" rx="2" fill="#444"/>')
    text(700, 912, '키스위치 (ARM)', 12, bold=True)
    KEY_L, KEY_R = (684, 1000), (716, 1000)
    a(f'<circle cx="{KEY_L[0]}" cy="{KEY_L[1]}" r="4" fill="#c9a227"/><circle cx="{KEY_R[0]}" cy="{KEY_R[1]}" r="4" fill="#c9a227"/>')
    flex(RP('D3'), KEY_L, '#8a5a2b', (420, 900), (684, 1060))
    flex(KEY_R, hole('B-32'), BLK, (760, 1060), (1202, 780)); used.add('B-32')
    a('<circle cx="880" cy="955" r="30" fill="#151515" filter="url(#sh)"/><circle cx="880" cy="955" r="6" fill="#333"/>')
    text(866, 930, '+', 14, c='#fff', bold=True)
    text(880, 912, '부저 (+ 표시가 D8)', 12, bold=True)
    BZ_P, BZ_N = (868, 990), (892, 990)
    a(f'<circle cx="{BZ_P[0]}" cy="{BZ_P[1]}" r="3.5" fill="#bbb"/><circle cx="{BZ_N[0]}" cy="{BZ_N[1]}" r="3.5" fill="#bbb"/>')
    flex(RP('D8'), BZ_P, '#e377c2', (470, 880), (868, 1050))
    flex(BZ_N, hole('B-33'), BLK, (900, 1050), (1224, 790)); used.add('B-33')
    for n, col in [('D8', '#a3307f'), ('D3', '#6b4220'), ('D2', '#555')]:
        wtext(372, RIGHT[n] - 4, n, 11, 'start', c=col, bold=True)
    steps.append(('공통', '키스위치', 'D3 → 키스위치 → 아래 − 레일 32열'))
    steps.append(('공통', '부저', 'D8 → 부저 + , 부저 − → 아래 − 레일 33열'))

else:
    flex(RP('D3'), hole('B-32'), '#8a5a2b', (430, 900), (1202, 800)); used.add('B-32')
    wtext(372, RIGHT['D3'] - 4, 'D3', 11, 'start', c='#6b4220', bold=True)
    wtext(1180, 760, 'D3 → GND (키스위치 대신 상시 아밍 허용)', 11, 'start', c='#6b4220', bold=True)
    steps.append(('공통', 'D3 (키스위치 대신)', 'D3 → 아래 − 레일 32열 점퍼. 아밍은 PC의 $A,1로만 한다'))
    steps.append(('공통', 'D2, D8', '비워 둔다 (실험자 E-STOP, 부저 생략)'))

# ------------------------------------------------------------------ 출력부 (위 오른쪽)
OR1, OR2 = '#ee7a1d', '#b5530f'
# TENS
a('<rect x="1050" y="96" width="180" height="150" rx="16" fill="#f7f7f5" stroke="#9a9a9a" stroke-width="2" filter="url(#sh)"/>')
a('<rect x="1072" y="112" width="136" height="54" rx="4" fill="#b9c7a9" stroke="#666"/>')
text(1140, 136, 'Normal 300µs', 11, c='#223'); text(1140, 154, '40Hz  C', 11, c='#223')
for kx in (1100, 1180):
    a(f'<circle cx="{kx}" cy="98" r="15" fill="#555" stroke="#222" stroke-width="2"/><line x1="{kx}" y1="98" x2="{kx}" y2="85" stroke="#eee" stroke-width="2"/>')
text(1100, 77, 'CH1', 10, bold=True); text(1180, 77, 'CH2', 10, bold=True)
text(1140, 200, 'TENS 7000', 14, bold=True); text(1140, 220, '9V 건전지 · 노브 스토퍼', 10, c='#555')
J1, J2 = (1100, 246), (1180, 246)
a(f'<circle cx="{J1[0]}" cy="{J1[1]}" r="6" fill="#222"/><circle cx="{J2[0]}" cy="{J2[1]}" r="6" fill="#222"/>')
# E-STOP
ES = {}
if not SIMPLE:
    a('<rect x="1290" y="70" width="156" height="120" rx="8" fill="#f1c40f" stroke="#a88a0b" stroke-width="2" filter="url(#sh)"/>')
    a('<circle cx="1368" cy="122" r="40" fill="#c0392b" stroke="#7d1f15" stroke-width="3"/><circle cx="1356" cy="110" r="12" fill="#e06b5e" opacity="0.6"/>')
    text(1368, 63, '실험자 E-STOP', 12, bold=True)
    blocks = {'NC1': 1295, 'NC2': 1345, 'NO': 1395}
    for nm, bxx in blocks.items():
        a(f'<rect x="{bxx}" y="192" width="44" height="30" rx="3" fill="#ddd" stroke="#888"/>')
        text(bxx + 22, 205, nm, 9, c='#c0392b' if nm.startswith('NC') else '#1f4f9e', bold=True)
        ES[nm] = ((bxx + 9, 216), (bxx + 35, 216))
        for p in ES[nm]: a(f'<circle cx="{p[0]}" cy="{p[1]}" r="3.5" fill="#c9a227" stroke="#7a5c10"/>')
# 참가자 STOP
a('<rect x="1490" y="92" width="120" height="100" rx="10" fill="#2b2b2b" filter="url(#sh)"/>')
a('<circle cx="1550" cy="135" r="28" fill="#27ae60" stroke="#145a32" stroke-width="3"/>')
text(1550, 85, '참가자 STOP', 12, bold=True)
PS = {}
for nm, bxx in {'NC1': 1494, 'NC2': 1552}.items():
    a(f'<rect x="{bxx}" y="194" width="54" height="26" rx="3" fill="#ddd" stroke="#888"/>')
    text(bxx + 27, 206, nm, 9, c='#c0392b', bold=True)
    PS[nm] = ((bxx + 10, 214), (bxx + 44, 214))
    for p in PS[nm]: a(f'<circle cx="{p[0]}" cy="{p[1]}" r="3.5" fill="#c9a227" stroke="#7a5c10"/>')
# 팔
a('<rect x="1680" y="90" width="120" height="190" rx="34" fill="#f2d4bd" stroke="#c99f80" stroke-width="2"/>')
a('<rect x="1830" y="90" width="140" height="190" rx="34" fill="#efcdb3" stroke="#c99f80" stroke-width="2"/>')
text(1740, 82, '전완 (손목 신전근)', 11, bold=True); text(1900, 82, '위팔 뒤 (삼두근)', 11, bold=True)
def pad(x, y, w, h, lab):
    a(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="6" fill="#8fa7bf" stroke="#44617e" stroke-width="2"/>')
    text(x, y + 4, lab, 10, c='#fff', bold=True)
    return (x, y + h / 2)
P1A, P1B = pad(1740, 130, 44, 44, 'A'), pad(1740, 225, 44, 44, 'B')
P2A, P2B = pad(1900, 135, 46, 72, 'A'), pad(1900, 235, 46, 72, 'B')
text(1795, 300, '패드 A = 근위(팔꿈치 쪽), B = 원위', 10, c='#555')

# 주황 배선
flex(J1, hole('a21'), OR1, (1100, 330), (960, 290)); wtext(1060, 300, 'CH1 리드 A', 10, c=OR2, bold=True)
flex(J2, hole('a51'), OR2, (1180, 330), (1620, 280)); wtext(1300, 330, 'CH2 리드 A', 10, c=OR2, bold=True)
flex(PS['NC1'][1], P1A, OR1, (1538, 290), (1740, 260), end2_pin=False)
flex((1108, 246), P1B, OR1, (1120, 300), (1740, 320), end2_pin=False)
flex(PS['NC2'][1], P2A, OR2, (1596, 290), (1900, 300), end2_pin=False)
flex((1188, 246), P2B, OR2, (1200, 320), (1900, 330), end2_pin=False)
if SIMPLE:
    flex(hole('a20'), PS['NC1'][0], OR1, (938, 280), (1504, 290))
    flex(hole('a50'), PS['NC2'][0], OR2, (1598, 270), (1562, 300))
    steps.append(('공통', '참가자 STOP (2NC)', 'NC1: a20 ↔ CH1 패드 A, NC2: a50 ↔ CH2 패드 A'))
else:
    flex(hole('a20'), ES['NC1'][0], OR1, (938, 280), (1304, 290))
    flex(ES['NC1'][1], PS['NC1'][0], OR1, (1330, 280), (1504, 280))
    flex(hole('a50'), ES['NC2'][0], OR2, (1598, 270), (1354, 300))
    flex(ES['NC2'][1], PS['NC2'][0], OR2, (1380, 280), (1562, 290))
    # E-STOP NO (저전압): D2와 GND
    flexpath(f'M345,670 Q400,670 400,725 L400,1210 Q400,1232 422,1232 L1963,1232 Q1985,1232 1985,1210 L1985,322 Q1985,300 1963,300 L1426,300 Q1404,300 1404,280 L1404,{ES["NO"][0][1]}', '#7f8c8d')
    wires.append(pin_end(*RP('D2'))); wires.append(pin_end(*ES['NO'][0]))
    flex(ES['NO'][1], hole('T-57'), BLK, (1440, 290), (1752, 280)); used.add('T-57')
    steps.append(('공통', '실험자 E-STOP', 'NC1: a20 ↔ 참가자 NC1 (CH1), NC2: a50 ↔ 참가자 NC2 (CH2), NO: 우노 D2 ↔ 위 − 레일 57열'))
    steps.append(('공통', '참가자 STOP', 'NC1: E-STOP NC1 ↔ CH1 패드 A, NC2: E-STOP NC2 ↔ CH2 패드 A'))

# ------------------------------------------------------------------ 범례·주의
a('<rect x="1010" y="850" width="955" height="265" rx="10" fill="#ffffff" stroke="#bdb6a6" stroke-width="1.5"/>')
text(1030, 878, '범례 · 꼭 지킬 것', 16, 'start', bold=True)
leg = [(RED, '5V'), (BLK, 'GND'), (YEL, '유지 신호 D9/D10'), (GRN, '트리거 D4/D7'), (BLU, '게이트 D5/D6'), ('#8e44ad', '보드 안 연결'), (OR1, 'TENS 출력 (사람에게 가는 선)')]
lx = 1030
for col, t in leg:
    a(f'<line x1="{lx}" y1="900" x2="{lx+26}" y2="900" stroke="{col}" stroke-width="6" stroke-linecap="round"/>')
    text(lx + 32, 904, t, 11.5, 'start'); lx += 32 + len(t) * 10.5 + 18
notes = [
    '1. 주황 점선 칸(20·21열, 50·51열의 위쪽 a~e)은 TENS 전용. 다른 부품·선 금지, 그 위의 레일 구멍(20~24, 50~54열)도 비워 둔다.',
    '2. 2N3904는 평평한 면이 가운데 홈 쪽. 노란 글자 E·B·C가 다리 위치다 (Q3·Q4는 E-B-C, Q1·Q2는 C-B-E 순서로 보임).',
    '3. TLC555와 AQY210EH는 홈(반달)이 왼쪽, 점이 1번 핀. 칩 아래쪽 줄(f)이 1번부터 시작한다.',
    ('4. 간소화판: D3은 GND에 상시 연결, D2·D8은 비워 둔다. 참가자 STOP(2NC)이 두 채널을 끊고, 실험자는 SPACE 키(전부 정지)를 맡는다.' if SIMPLE else
     '4. 2채널을 비상정지 하나로 동시에 끊으려면 E-STOP에 NC 접점 블록 1개를 추가하고, 참가자 STOP도 2NC로 준비한다.'),
    '5. 첫 테스트는 TENS 대신 a20·a21에 건전지 + LED + 1kΩ을 걸어 깜빡임만 본다. 우노 GND와 연결하지 않는다.',
    '6. 전극은 팔에만. 가슴·목·머리 금지, 양팔에 걸친 배치 금지. 사람 연결은 GUIDE.md 벤치 검사 통과 후.',
    '7. 꽂는 위치 전체 목록: docs/BREADBOARD' + SUF + '.md',
]
for i, t in enumerate(notes):
    text(1030, 934 + i * 25, t, 12, 'start', c='#d62728' if i == 5 else '#333', bold=(i == 5))

o.extend(wires)
o.append('</svg>')
io.open(os.path.join(DOCS, 'breadboard_830' + SUF + '.svg'), 'w', encoding='utf-8').write('\n'.join(o))

# ------------------------------------------------------------------ markdown
md = ['# 브레드보드 꽂는 위치 목록 (830홀, 우노, 2채널 v2)' + (' — 간소화판 (키스위치·부저·실험자 E-STOP 생략)' if SIMPLE else ''), '',
      '그림: [breadboard_830' + SUF + '.png](breadboard_830' + SUF + '.png). 열 번호 1~63, 행 a~j. 위쪽 레일은 바깥쪽 빨강 줄이 +5V, 안쪽 파랑 줄이 GND. 아래쪽은 안쪽 파랑이 GND, 바깥쪽 빨강이 +5V.',
      '', '레일 구멍은 5개씩 묶여 있고 7·13·19·25·31·37·43·49·55·61열 자리는 비어 있다.', '']
for grp in ['공통', 'CH1', 'CH2']:
    md.append(f'## {grp}' + (' (손목 신전근: 트리거 D4, 게이트 D5, 유지 D9)' if grp == 'CH1' else ' (삼두근: 트리거 D7, 게이트 D6, 유지 D10)' if grp == 'CH2' else ''))
    md.append(''); md.append('| 부품 | 위치 |'); md.append('|---|---|')
    for g, what, where in steps:
        if g == grp: md.append(f'| {what} | {where} |')
    md.append('')
md += ['## 조립 순서', '',
       '1. 레일: 우노 5V·GND를 위 레일에, 59·60열에서 위아래 레일을 잇는다.',
       '2. CH1의 TLC555와 AQY210EH를 가운데 홈에 걸쳐 꽂는다 (홈이 왼쪽).',
       '3. 저항·커패시터 → 트랜지스터 → 보드 안 점퍼 순서.',
       '4. 우노 신호선(D9, D4, D5)을 꽂고 GUIDE.md 4.3 LED 검사.',
       '5. 통과하면 CH2를 30열 오른쪽에 똑같이 복제 (D10, D7, D6).',
       ('6. 마지막에 참가자 STOP·TENS 출력(주황). 실험자는 SPACE 키를 맡는다.' if SIMPLE else '6. 마지막에 비상정지·참가자 STOP·TENS 출력(주황).'), '']
io.open(os.path.join(DOCS, 'BREADBOARD' + SUF + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
print('ok', len(used), 'holes')
