"""멀티미터로 PhotoMOS 출력(a20·a21) 확인하는 법 그림."""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1500, 1060
F = 'font-family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"'
o = []
def a(s): o.append(s)
def t(x, y, s, size=16, anchor='middle', c='#222', bold=False):
    b = 'font-weight="700"' if bold else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {b}>{s}</text>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><filter id="sh"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-opacity="0.25"/></filter></defs>')
a(f'<rect width="{W}" height="{H}" fill="#ece9e2"/>')
t(40, 50, '멀티미터로 PhotoMOS 확인하기 — a20 · a21 (CH1)', 28, 'start', bold=True)
t(40, 82, 'TENS는 연결하지 않은 상태. 브레드보드 20~21열 근처를 확대한 그림', 16, 'start', c='#555')

# ---------------- zoomed breadboard: columns 16..25
P = 54; X0 = 120
cols = list(range(16, 26))
def cx(c): return X0 + (c - 16) * P
DY = 70
ROW = {k: v + DY for k, v in {'a': 300, 'b': 354, 'c': 408, 'd': 462, 'e': 516, 'f': 600, 'g': 654, 'h': 708, 'i': 762, 'j': 816}.items()}
RT, RB = 200 + DY, 238 + DY
a(f'<rect x="{X0-50}" y="{170+DY}" width="{cx(25)-X0+100}" height="690" rx="14" fill="#f7f5ef" stroke="#cfc9bb" stroke-width="2" filter="url(#sh)"/>')
a(f'<rect x="{X0-40}" y="{549+DY}" width="{cx(25)-X0+80}" height="20" rx="4" fill="#dcd6c8"/>')
a(f'<line x1="{X0-36}" y1="{RT-18}" x2="{cx(25)+36}" y2="{RT-18}" stroke="#d62728" stroke-width="3"/>')
a(f'<line x1="{X0-36}" y1="{RB+18}" x2="{cx(25)+36}" y2="{RB+18}" stroke="#2f6fd6" stroke-width="3"/>')
t(X0 - 30, RT + 6, '+', 20, c='#d62728', bold=True); t(X0 - 30, RB + 6, '−', 20, c='#2f6fd6', bold=True)
# highlighted strips col20/21 a-e
for c, col in ((20, '#ff8a3d'), (21, '#ff8a3d')):
    a(f'<rect x="{cx(c)-20}" y="{ROW["a"]-22}" width="40" height="{ROW["e"]-ROW["a"]+44}" rx="8" fill="{col}33" stroke="{col}" stroke-width="2.5" stroke-dasharray="6,4"/>')
def hole(x, y, hl=False):
    fill = '#3b3b3b'
    a(f'<rect x="{x-8}" y="{y-8}" width="16" height="16" rx="3" fill="{fill}" stroke="#9b9586" stroke-width="1.5"/>')
for c in cols:
    for r, y in ROW.items(): hole(cx(c), y)
    if c not in (19, 25):
        hole(cx(c), RT); hole(cx(c), RB)
    t(cx(c), 280 + DY, str(c), 15, c='#8a8473', bold=c in (20, 21))
    t(cx(c), 846 + DY, str(c), 13, c='#8a8473')
for r, y in ROW.items():
    t(X0 - 34, y + 6, r, 16, c='#8a8473', bold=r == 'a')
# AQY chip e20-21 / f20-21
xl, xr = cx(20) - 26, cx(21) + 26
a(f'<rect x="{xl}" y="{505+DY}" width="{xr-xl}" height="106" rx="6" fill="#1c1c1c" filter="url(#sh)"/>')
a(f'<path d="M{xl},{545+DY} a14,14 0 0 1 0,28" fill="#444"/>')
a(f'<circle cx="{xl+14}" cy="{595+DY}" r="5" fill="#888"/>')
t((xl + xr) / 2, 556 + DY, 'AQY', 17, c='#eee', bold=True); t((xl + xr) / 2, 576 + DY, '210EH', 15, c='#eee', bold=True)
t(cx(20), 530 + DY, '4', 13, c='#ffb070', bold=True); t(cx(21), 530 + DY, '3', 13, c='#ffb070', bold=True)
t(cx(20), 600 + DY, '1', 13, c='#bbb', bold=True); t(cx(21), 600 + DY, '2', 13, c='#bbb', bold=True)
# existing low-voltage jumpers (faded) to give context
a(f'<line x1="{cx(16)}" y1="{ROW["h"]}" x2="{cx(20)}" y2="{ROW["h"]}" stroke="#8e44ad" stroke-width="9" stroke-linecap="round" opacity="0.55"/>')
a(f'<line x1="{cx(23)}" y1="{ROW["h"]}" x2="{cx(21)}" y2="{ROW["h"]}" stroke="#8e44ad" stroke-width="9" stroke-linecap="round" opacity="0.55"/>')
t(cx(18), ROW['h'] + 34, '(이미 꽂혀 있는 보라 점퍼)', 12, c='#7d5a8c')

# jumper wires from a20 / a21 -> pins pointing right, above the board
def jumper(x, y, x2, y2, col):
    d = f'M{x},{y} C{x},{y-120} {x2-160},{y2} {x2-26},{y2}'
    a(f'<path d="{d}" fill="none" stroke="#00000044" stroke-width="13" stroke-linecap="round"/>')
    a(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round"/>')
    a(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" rx="2" fill="#ccc" stroke="#555"/>')
    a(f'<rect x="{x2-28}" y="{y2-8}" width="28" height="16" rx="3" fill="#222"/>')
    a(f'<rect x="{x2}" y="{y2-2}" width="20" height="4" fill="#c9c9c9"/>')
    return (x2 + 20, y2)
JA = jumper(cx(20), ROW['a'], 700, 150, '#f1f1f1')
JB = jumper(cx(21), ROW['a'], 700, 225, '#f2c12e')
t(cx(20) - 4, ROW['a'] - 34, 'a20', 18, 'end', c='#c4560f', bold=True)
t(cx(21) + 6, ROW['a'] - 34, 'a21', 18, 'start', c='#c4560f', bold=True)
t(560, 128, '수-수 점퍼 2개', 14, c='#555', bold=True)

def probe(tip, col):
    x, y = tip
    a(f'<line x1="{x}" y1="{y}" x2="{x+40}" y2="{y}" stroke="#bbb" stroke-width="5" stroke-linecap="round"/>')
    a(f'<rect x="{x+40}" y="{y-11}" width="92" height="22" rx="9" fill="{col}"/>')
    a(f'<circle cx="{x}" cy="{y}" r="10" fill="none" stroke="#2e9e4f" stroke-width="3"/>')
    return (x + 132, y)
PA = probe(JA, '#d62728')
PB = probe(JB, '#222')
t(790, 116, '프로브 끝을 점퍼 핀에 댄다', 14, c='#1d6b35', bold=True)
# ---------------- multimeter
MX, MY = 900, 200
a(f'<rect x="{MX}" y="{MY}" width="250" height="420" rx="26" fill="#f2b51f" stroke="#a87b10" stroke-width="3" filter="url(#sh)"/>')
a(f'<rect x="{MX+20}" y="{MY+18}" width="210" height="390" rx="18" fill="#2b2b2b"/>')
a(f'<rect x="{MX+40}" y="{MY+38}" width="170" height="80" rx="6" fill="#b9c7a9" stroke="#556"/>')
t(MX + 125, MY + 92, '0.000', 34, c='#223', bold=True)
a(f'<text x="{MX+190}" y="{MY+60}" font-size="18" fill="#223">🔊</text>')
dcx, dcy = MX + 125, MY + 220
a(f'<circle cx="{dcx}" cy="{dcy}" r="62" fill="#3d3d3d" stroke="#111" stroke-width="3"/>')
for ang, lab in [(-150, 'OFF'), (-110, 'V⎓'), (-70, 'V~'), (-30, 'Ω'), (20, '🔊'), (60, 'A')]:
    import math
    r = 82; x = dcx + r * math.cos(math.radians(ang)); y = dcy + r * math.sin(math.radians(ang))
    t(x, y + 5, lab, 14, c='#ffd54a' if lab == '🔊' else '#ddd', bold=lab == '🔊')
a(f'<line x1="{dcx}" y1="{dcy}" x2="{dcx + 55*math.cos(math.radians(20))}" y2="{dcy + 55*math.sin(math.radians(20))}" stroke="#ffd54a" stroke-width="8" stroke-linecap="round"/>')
t(dcx, dcy + 104, '다이얼 → 부저(🔊 또는 •)))', 13, c='#ffd54a', bold=True)
jacks = [('10A', MX + 60, '#888'), ('COM', MX + 125, '#111'), ('VΩ', MX + 190, '#d62728')]
for lab, x, col in jacks:
    a(f'<circle cx="{x}" cy="{MY+370}" r="15" fill="#111" stroke="{col}" stroke-width="4"/>')
    t(x, MY + 405, lab, 13, c='#eee', bold=True)
a(f'<line x1="{MX+48}" y1="{MY+358}" x2="{MX+72}" y2="{MY+382}" stroke="#e74c3c" stroke-width="4"/><line x1="{MX+72}" y1="{MY+358}" x2="{MX+48}" y2="{MY+382}" stroke="#e74c3c" stroke-width="4"/>')
# probe cables to jacks
a(f'<path d="M{PA[0]},{PA[1]} C{PA[0]+60},{PA[1]} {MX-40},{MY+560} {MX+190},{MY+520} S{MX+190},{MY+430} {MX+190},{MY+385}" fill="none" stroke="#d62728" stroke-width="6"/>')
a(f'<path d="M{PB[0]},{PB[1]} C{PB[0]+40},{PB[1]} {MX-60},{MY+530} {MX+125},{MY+505} S{MX+125},{MY+430} {MX+125},{MY+385}" fill="none" stroke="#222" stroke-width="6"/>')
t(MX + 125, MY + 548, '검정 → COM, 빨강 → VΩ', 14, bold=True)
t(MX + 125, MY + 568, '10A 구멍은 쓰지 않는다', 13, c='#c0392b', bold=True)

# ---------------- explanation box
BX, BY = 1180, 200
a(f'<rect x="{BX}" y="{BY}" width="295" height="420" rx="12" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
lines = [('왜 a20·a21인가', True, '#222'),
         ('세로줄 a~e 다섯 칸은', False, '#333'), ('보드 안에서 서로 이어져 있다.', False, '#333'),
         ('그래서 a20 = PhotoMOS 4번,', False, '#333'), ('a21 = PhotoMOS 3번과 같은 점.', False, '#333'),
         ('', False, '#333'),
         ('PhotoMOS는 스위치다', True, '#222'),
         ('켜지면 3번·4번이 연결되어', False, '#333'), ('멀티미터가 삐 하고 운다.', False, '#333'),
         ('꺼지면 끊겨서 조용하다.', False, '#333'),
         ('', False, '#333'),
         ('프로브가 구멍에 안 들어가면', True, '#222'),
         ('수-수 점퍼를 a20·a21에 꽂고', False, '#333'), ('점퍼 반대쪽 핀에 댄다.', False, '#333'),
         ('악어클립이 있으면 물리면 편하다.', False, '#333')]
for i, (s, b, c) in enumerate(lines):
    t(BX + 18, BY + 34 + i * 25, s, 15 if b else 14, 'start', c=c, bold=b)

# ---------------- steps
SX, SY = 690, 790
a(f'<rect x="{SX}" y="{SY}" width="785" height="262" rx="12" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
t(SX + 20, SY + 36, '순서', 20, 'start', bold=True)
steps = [
    '1. 멀티미터 검정 리드 → COM, 빨강 리드 → VΩ. 다이얼을 부저(🔊)로.',
    '2. 리드 끝 두 개를 서로 맞대 본다 → 삐 소리가 나면 멀티미터 정상.',
    '3. 수-수 점퍼 2개를 a20, a21에 꽂고, 빨강·검정 프로브를 각각 점퍼 끝에 댄다.',
    '   (지금은 조용해야 정상. 소리가 나면 PhotoMOS가 계속 켜진 것이니 알려 주기)',
    '4. 터미널에서 실행:  python C:\\Users\\wotjr\\ems-recoil-sim\\tools\\ssr_blink.py COM11 1',
    '5. 화면에 "켬"이 뜬 2초 → 삐,  "끔"이 뜬 2초 → 조용.  8번 반복되면 CH1 정상.',
    '6. CH2는 a50 · a51에 같은 방법으로 대고, 명령 끝의 1을 2로 바꿔 실행.',
]
for i, s in enumerate(steps):
    t(SX + 24, SY + 70 + i * 26, s, 14.5, 'start', c='#7a7a7a' if s.startswith('   ') else '#222')
t(SX + 24, SY + 70 + 7 * 26 + 4, '빨강·검정 방향은 상관없다. 부저 모드는 연결됐는지만 본다.', 14, 'start', c='#1d6b35', bold=True)

a('</svg>')
io.open(os.path.join(HERE, '..', 'docs', 'probe_a20_a21.svg'), 'w', encoding='utf-8').write('\n'.join(o))
print('ok')
