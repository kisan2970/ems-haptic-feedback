"""출력부(TENS 측) 실물 연결 그림 — 간소화판(실험자 E-STOP 없음), CH1."""
import io, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1600, 1160
F = 'font-family="Malgun Gothic, Apple SD Gothic Neo, WenQuanYi Zen Hei, sans-serif"'
o = []
def a(s): o.append(s)
def t(x, y, s, size=16, anchor='middle', c='#222', bold=False):
    b = 'font-weight="700"' if bold else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {b}>{s}</text>')
def wire(d, col, w=8):
    a(f'<path d="{d}" fill="none" stroke="#00000040" stroke-width="{w+4}" stroke-linecap="round"/>')
    a(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
def splice(x, y, label):
    # 꼰 연결 + 절연테이프
    a(f'<rect x="{x-26}" y="{y-13}" width="52" height="26" rx="6" fill="#2b2b2b" stroke="#000"/>')
    for k in range(-18, 20, 8):
        a(f'<line x1="{x+k}" y1="{y-13}" x2="{x+k+6}" y2="{y+13}" stroke="#555" stroke-width="2"/>')
    t(x, y - 22, label, 13, c='#444', bold=True)

RED, BLK, ORG = '#d62728', '#262626', '#ff8a3d'
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><filter id="sh"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-opacity="0.25"/></filter></defs>')
a(f'<rect width="{W}" height="{H}" fill="#ece9e2"/>')
t(40, 50, '출력부 실물 연결 — 간소화판 v2.2 (강도 사다리), CH1', 28, 'start', bold=True)
t(40, 82, 'TENS 리드 A(빨강)를 잘라 a21로 넣고 a26에서 참가자 STOP으로 뺀다. 리드 B(검정)는 그대로 패드로. 작업은 TENS 전원 OFF · 9V 건전지를 뺀 상태에서.', 16, 'start', c='#555')

# ---------------- TENS 7000
TX, TY = 60, 130
a(f'<rect x="{TX}" y="{TY}" width="230" height="330" rx="28" fill="#f4f4f6" stroke="#9aa" stroke-width="3" filter="url(#sh)"/>')
a(f'<rect x="{TX+30}" y="{TY+30}" width="170" height="80" rx="8" fill="#b9c7a9" stroke="#556"/>')
t(TX + 115, TY + 80, 'TENS 7000', 22, c='#223', bold=True)
for i, (lab, x) in enumerate((('CH1', TX + 70), ('CH2', TX + 160))):
    a(f'<circle cx="{x}" cy="{TY+175}" r="30" fill="#ddd" stroke="#777" stroke-width="3"/>')
    a(f'<circle cx="{x}" cy="{TY+175}" r="8" fill="#555"/>')
    t(x, TY + 225, lab, 15, c='#333', bold=True)
t(TX + 115, TY + 265, '노브 0 · Normal', 14, c='#555')
t(TX + 115, TY + 287, '300µs · 40Hz', 14, c='#555')
# 리드 플러그 (CH1 바닥 잭)
JX, JY = TX + 70, TY + 330
a(f'<rect x="{JX-12}" y="{JY}" width="24" height="44" rx="5" fill="#333"/>')
t(JX - 22, JY + 30, '2.35mm 플러그', 13, 'end', c='#555')
# 분기점
SX, SY = JX, 570
wire(f'M{JX},{JY+44} L{SX},{SY}', '#555', 12)
a(f'<rect x="{SX-14}" y="{SY-6}" width="28" height="22" rx="5" fill="#444"/>')
t(SX + 24, SY + 50, '예비 리드선 (동봉품은 자르지 않는다)', 13, 'start', c='#555')

# ---------------- 확대한 브레드보드 (14~28열)
P = 34; X0 = 520; C0, C1 = 14, 28
cols = list(range(C0, C1 + 1))
def cx(c): return X0 + (c - C0) * P
ROW = {'a': 360, 'b': 405, 'c': 450, 'd': 495, 'e': 540, 'f': 615, 'g': 660, 'h': 705, 'i': 750, 'j': 795}
RT, RB = 270, 305
a(f'<rect x="{X0-46}" y="230" width="{cx(C1)-X0+92}" height="610" rx="14" fill="#f7f5ef" stroke="#cfc9bb" stroke-width="2" filter="url(#sh)"/>')
a(f'<rect x="{X0-36}" y="567" width="{cx(C1)-X0+72}" height="20" rx="4" fill="#dcd6c8"/>')
a(f'<line x1="{X0-32}" y1="{RT-16}" x2="{cx(C1)+32}" y2="{RT-16}" stroke="#d62728" stroke-width="3"/>')
a(f'<line x1="{X0-32}" y1="{RB+16}" x2="{cx(C1)+32}" y2="{RB+16}" stroke="#2f6fd6" stroke-width="3"/>')
# TENS 전용 영역: 위쪽 a~e 17~27열
a(f'<rect x="{cx(17)-16}" y="{ROW["a"]-20}" width="{cx(27)-cx(17)+32}" height="{ROW["e"]-ROW["a"]+40}" rx="8" fill="{ORG}22" stroke="{ORG}" stroke-width="2.5" stroke-dasharray="6,4"/>')
def hole(x, y):
    a(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" rx="3" fill="#3b3b3b" stroke="#9b9586" stroke-width="1.5"/>')
for c in cols:
    for r, y in ROW.items(): hole(cx(c), y)
    if c not in (19, 25): hole(cx(c), RT); hole(cx(c), RB)
    t(cx(c), 340, str(c), 12, c='#c4560f' if c in (17, 20, 21, 23, 26, 27) else '#8a8473', bold=c in (21, 26))
for r, y in ROW.items(): t(X0 - 30, y + 5, r, 14, c='#8a8473', bold=r == 'a')
def chip(c, title):
    xl, xr = cx(c) - 17, cx(c + 1) + 17
    a(f'<rect x="{xl}" y="530" width="{xr-xl}" height="96" rx="6" fill="#1c1c1c" filter="url(#sh)"/>')
    a(f'<path d="M{xl},566 a11,11 0 0 1 0,22" fill="#444"/>')
    t((xl + xr) / 2, 576, 'AQY', 12, c='#eee', bold=True); t((xl + xr) / 2, 592, title, 11, c='#ffb070', bold=True)
    t(cx(c), 553, '4', 11, c='#ffb070', bold=True); t(cx(c + 1), 553, '3', 11, c='#ffb070', bold=True)
chip(17, 'LA'); chip(20, '게이팅'); chip(26, 'LB')
def res(c1, c2, row, val, faded=False):
    x1, x2, y = cx(c1), cx(c2), ROW[row]
    op = ' opacity="0.45"' if faded else ''
    a(f'<g{op}><line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#9a9a9a" stroke-width="3"/>'
      f'<rect x="{(x1+x2)/2-22}" y="{y-9}" width="44" height="18" rx="8" fill="#8ec2e6" stroke="#4f7fa3" stroke-width="1.5"/>'
      f'<rect x="{x1-4}" y="{y-4}" width="8" height="8" fill="#ccc" stroke="#555"/><rect x="{x2-4}" y="{y-4}" width="8" height="8" fill="#ccc" stroke="#555"/></g>')
    if not faded:
        a(f'<rect x="{(x1+x2)/2-30}" y="{y-34}" width="60" height="20" rx="5" fill="#fffbe6" stroke="#bbb"/>')
        t((x1 + x2) / 2, y - 19, val, 13, c='#222', bold=True)
def jump(c1, r1, c2, r2, col, faded=False):
    op = 0.45 if faded else 1
    a(f'<line x1="{cx(c1)}" y1="{ROW[r1]}" x2="{cx(c2)}" y2="{ROW[r2]}" stroke="{col}" stroke-width="7" stroke-linecap="round" opacity="{op}"/>')
# 위쪽(TENS 쪽) 사다리: 20열 → R1 → 17열 → (점퍼) 23열 → R2 → 26열
res(17, 20, 'b', '470Ω R1')
jump(18, 'c', 20, 'c', ORG)
jump(17, 'a', 23, 'a', ORG)
res(23, 26, 'b', '1kΩ R2')
jump(23, 'c', 27, 'c', ORG)
# 아래쪽(저전압) 흐리게: 기존 점퍼 + 사다리 LED 구동
jump(16, 'h', 20, 'h', '#8e44ad', True); jump(23, 'h', 21, 'h', '#8e44ad', True)
res(14, 17, 'i', '', True); res(22, 26, 'g', '', True)
jump(18, 'j', 18, 'j', '#222', True); jump(27, 'j', 27, 'j', '#222', True)
t((X0 + cx(C1)) / 2, 866, '아래쪽 f~j: 저전압 회로 (사다리 LED 구동 330Ω 포함, 배치도대로 이미 조립)', 13, c='#7d5a8c')
# 경로 설명
a(f'<rect x="{X0-56}" y="102" width="{cx(C1)-X0+112}" height="30" rx="8" fill="#fff" stroke="#c4560f"/>')
t((X0 + cx(C1)) / 2, 123, 'a21 → 게이팅 PhotoMOS → 20열 → R1 470Ω → 17열 → R2 1kΩ → 26열(a26) → STOP', 14, c='#c4560f', bold=True)

def pin(x, y):
    a(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" rx="2" fill="#ccc" stroke="#555"/>')

# ---------------- 빨강 기기 쪽 반 → 꼬아 잇기 → 점퍼 → a21
SPL1 = (440, 190)
wire(f'M{SX+14},{SY+4} L330,{SY+4} C410,{SY+4} 410,{SY-40} 410,{SY-120} L410,{SPL1[1]+50} C410,{SPL1[1]+10} {SPL1[0]-40},{SPL1[1]} {SPL1[0]-26},{SPL1[1]}', RED)
splice(*SPL1, '꼬아 감고 테이프')
wire(f'M{SPL1[0]+26},{SPL1[1]} C{SPL1[0]+260},{SPL1[1]} {cx(21)},{ROW["a"]-150} {cx(21)},{ROW["a"]}', ORG)
pin(cx(21), ROW['a'])
t(160, 500, '① 빨강(리드 A) 기기 쪽 반', 15, 'start', c=RED, bold=True)
t(160, 520, '    + 수-수 점퍼 반쪽 → a21', 14, 'start', c='#444')

# ---------------- 참가자 STOP (NC 11·12)
BX, BY = 1150, 140
a(f'<rect x="{BX}" y="{BY}" width="300" height="250" rx="16" fill="#3a3a3a" filter="url(#sh)"/>')
a(f'<circle cx="{BX+150}" cy="{BY+70}" r="46" fill="#e8b500" stroke="#8a6b00" stroke-width="4"/>')
t(BX + 150, BY + 77, 'STOP', 20, c='#3a2a00', bold=True)
t(BX + 150, BY - 12, '참가자 STOP 버튼 (손에 쥐는 쪽)', 15, c='#222', bold=True)
TERM = {'11': (BX + 50, BY + 175), '12': (BX + 110, BY + 175), '23': (BX + 190, BY + 175), '24': (BX + 250, BY + 175)}
a(f'<rect x="{BX+22}" y="{BY+136}" width="116" height="62" rx="8" fill="#5b8f5b"/>')
a(f'<rect x="{BX+162}" y="{BY+136}" width="116" height="62" rx="8" fill="#6a6a6a" opacity="0.6"/>')
for k, (x, y) in TERM.items():
    a(f'<circle cx="{x}" cy="{y}" r="13" fill="#d8c27a" stroke="#555" stroke-width="2"/>')
    a(f'<line x1="{x-8}" y1="{y}" x2="{x+8}" y2="{y}" stroke="#555" stroke-width="3"/>')
    t(x, y - 20, k, 14, c='#fff', bold=True)
t(BX + 80, BY + 128, 'NC (평소 연결)', 13, c='#d6f5d6', bold=True)
t(BX + 220, BY + 128, 'NO — 쓰지 않음', 13, c='#ddd')

# ---------------- a26 → 점퍼 → STOP 11
wire(f'M{cx(26)},{ROW["a"]} L{cx(26)},245 C{cx(26)},215 {cx(26)+30},212 {cx(26)+60},212 L1090,212 C1140,212 1150,{TERM["11"][1]} {TERM["11"][0]},{TERM["11"][1]}', ORG)
pin(cx(26), ROW['a'])
t(885, 196, '② 수-수 점퍼 반쪽: a26 → STOP 11번', 15, 'start', c='#c4560f', bold=True)

# a21 · a26 라벨 (선 위에 보이도록 마지막에)
for c, x, anc in ((21, cx(21) + 14, 'start'), (26, cx(26) + 14, 'start')):
    w = 46; rx = x - w if anc == 'end' else x
    a(f'<rect x="{rx}" y="{ROW["a"]+10}" width="{w}" height="24" rx="6" fill="#fff" stroke="#c4560f" stroke-width="2"/>')
    t(rx + w / 2, ROW['a'] + 28, f'a{c}', 16, c='#c4560f', bold=True)

# ---------------- 팔과 패드
AY = 960
a(f'<path d="M1010,{AY-48} C1150,{AY-70} 1420,{AY-80} 1560,{AY-60} L1560,{AY+62} C1420,{AY+80} 1150,{AY+64} 1010,{AY+46} Z" fill="#f1c9a5" stroke="#c99a74" stroke-width="3"/>')
a(f'<ellipse cx="985" cy="{AY}" rx="45" ry="52" fill="#f1c9a5" stroke="#c99a74" stroke-width="3"/>')
t(985, AY + 6, '손', 15, c='#8a5a3a', bold=True)
t(1545, AY - 78, '팔꿈치 쪽 →', 14, 'end', c='#8a5a3a', bold=True)
PA, PB = (1380, AY - 6), (1150, AY - 2)
for (x, y), lab in ((PA, '패드 A'), (PB, '패드 B')):
    a(f'<rect x="{x-50}" y="{y-34}" width="100" height="68" rx="10" fill="#9fd3f2" stroke="#2c7fb8" stroke-width="3" opacity="0.95"/>')
    a(f'<circle cx="{x}" cy="{y}" r="9" fill="#2c7fb8"/>')
    t(x, y + 58, lab, 15, c='#1d5a85', bold=True)
t(1265, AY + 105, '손등 쪽 전완(손목 신전근): A는 팔꿈치 바깥 뼈에서 5cm, B는 그보다 8cm 손목 쪽', 13, c='#5a3a2a')

# ---------------- STOP 12 → 빨강 패드 쪽 반 → 패드 A
SPL2 = (TERM['12'][0] + 90, 520)
wire(f'M{TERM["12"][0]},{TERM["12"][1]} C{TERM["12"][0]},{SPL2[1]-60} {SPL2[0]-60},{SPL2[1]} {SPL2[0]},{SPL2[1]}', RED)
wire(f'M{SPL2[0]},{SPL2[1]} C{SPL2[0]+120},{SPL2[1]+40} {PA[0]},{PA[1]-220} {PA[0]},{PA[1]}', RED)
t(1335, 640, '③ 빨강(리드 A) 패드 쪽 반', 15, 'end', c=RED, bold=True)
t(1335, 662, '벗긴 끝 → STOP 12번, 핀 → 패드 A', 14, 'end', c='#444')

# ---------------- 검정 → 패드 B (자르지 않음)
wire(f'M{SX-4},{SY+16} L{SX-4},{840} C{SX-4},{875} {SX+40},{885} {SX+80},{885} L{PB[0]-120},{885} C{PB[0]-40},{885} {PB[0]},{PB[1]-60} {PB[0]},{PB[1]}', BLK)
t(SX + 100, 873, '④ 검정(리드 B): 자르지 않고 그대로 패드 B', 15, 'start', c=BLK, bold=True)

# ---------------- 확인 목록
QX, QY = 60, 980
a(f'<rect x="{QX}" y="{QY}" width="860" height="160" rx="12" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
t(QX + 20, QY + 32, '확인', 18, 'start', bold=True)
checks = [
    '• 17~27열 위쪽(a~e)은 TENS 쪽: 리드선·사다리 저항·주황 점퍼만. 우노 핀·GND·레일에 닿으면 안 된다.',
    '• 꼰 부분, 단자, 노출된 구리는 전부 절연테이프. 주황·빨강 선은 USB·IMU 선과 떨어뜨린다.',
    '• 실험자 E-STOP이 없으니 실험자는 노트북 SPACE(전부 정지), 참가자는 STOP 버튼을 쥔다.',
    '• 멀티미터 절연 확인과 1kΩ 벤치 비교 전에는 이 경로를 사람에게 연결하지 않는다.',
    '• CH2는 30열 오른쪽(a51 입력, a56 출력). 세기 단계는 $L,1,0~3 (부팅 3 = 노브 세기, 0 = 가장 약함).',
]
for i, s in enumerate(checks):
    t(QX + 24, QY + 60 + i * 21, s, 14, 'start', c='#c0392b' if i == 3 else '#222', bold=i == 3)

a('</svg>')
svg = os.path.join(HERE, '..', 'docs', 'output_wiring_simple.svg')
io.open(svg, 'w', encoding='utf-8').write('\n'.join(o))
print('ok', os.path.abspath(svg))
