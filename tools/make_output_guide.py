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
t(40, 50, '출력부 실물 연결 — 간소화판 (실험자 E-STOP 없음), CH1', 28, 'start', bold=True)
t(40, 82, 'TENS 리드 A(빨강)를 잘라 PhotoMOS와 참가자 STOP을 거치게 하고, 리드 B(검정)는 그대로 패드로. 작업은 TENS 전원 OFF · 9V 건전지를 뺀 상태에서.', 16, 'start', c='#555')

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

# ---------------- 확대한 브레드보드 (16~25열)
P = 50; X0 = 560
cols = list(range(16, 26))
def cx(c): return X0 + (c - 16) * P
ROW = {'a': 360, 'b': 405, 'c': 450, 'd': 495, 'e': 540, 'f': 615, 'g': 660, 'h': 705, 'i': 750, 'j': 795}
RT, RB = 270, 305
a(f'<rect x="{X0-50}" y="230" width="{cx(25)-X0+100}" height="610" rx="14" fill="#f7f5ef" stroke="#cfc9bb" stroke-width="2" filter="url(#sh)"/>')
a(f'<rect x="{X0-40}" y="567" width="{cx(25)-X0+80}" height="20" rx="4" fill="#dcd6c8"/>')
a(f'<line x1="{X0-36}" y1="{RT-16}" x2="{cx(25)+36}" y2="{RT-16}" stroke="#d62728" stroke-width="3"/>')
a(f'<line x1="{X0-36}" y1="{RB+16}" x2="{cx(25)+36}" y2="{RB+16}" stroke="#2f6fd6" stroke-width="3"/>')
for c in (20, 21):
    a(f'<rect x="{cx(c)-19}" y="{ROW["a"]-20}" width="38" height="{ROW["e"]-ROW["a"]+40}" rx="8" fill="{ORG}33" stroke="{ORG}" stroke-width="2.5" stroke-dasharray="6,4"/>')
def hole(x, y):
    a(f'<rect x="{x-7}" y="{y-7}" width="14" height="14" rx="3" fill="#3b3b3b" stroke="#9b9586" stroke-width="1.5"/>')
for c in cols:
    for r, y in ROW.items(): hole(cx(c), y)
    if c not in (19, 25): hole(cx(c), RT); hole(cx(c), RB)
    t(cx(c), 340, str(c), 14, c='#8a8473', bold=c in (20, 21))
for r, y in ROW.items(): t(X0 - 32, y + 6, r, 15, c='#8a8473', bold=r == 'a')
xl, xr = cx(20) - 24, cx(21) + 24
a(f'<rect x="{xl}" y="530" width="{xr-xl}" height="96" rx="6" fill="#1c1c1c" filter="url(#sh)"/>')
a(f'<path d="M{xl},564 a13,13 0 0 1 0,26" fill="#444"/>')
t((xl + xr) / 2, 574, 'AQY', 15, c='#eee', bold=True); t((xl + xr) / 2, 592, '210EH', 13, c='#eee', bold=True)
t(cx(20), 553, '4', 12, c='#ffb070', bold=True); t(cx(21), 553, '3', 12, c='#ffb070', bold=True)
t(cx(20), 620, '1', 12, c='#bbb', bold=True); t(cx(21), 620, '2', 12, c='#bbb', bold=True)
# 이미 꽂힌 저전압 점퍼 (흐리게)
a(f'<line x1="{cx(16)}" y1="{ROW["h"]}" x2="{cx(20)}" y2="{ROW["h"]}" stroke="#8e44ad" stroke-width="8" stroke-linecap="round" opacity="0.5"/>')
a(f'<line x1="{cx(23)}" y1="{ROW["h"]}" x2="{cx(21)}" y2="{ROW["h"]}" stroke="#8e44ad" stroke-width="8" stroke-linecap="round" opacity="0.5"/>')
t((X0 + cx(25)) / 2, 866, '아래쪽 f~j는 이미 조립된 저전압 회로 (건드리지 않음)', 13, c='#7d5a8c')
# b~e 20·21은 비어 있어야 함
a(f'<rect x="{cx(22)-22}" y="{ROW["c"]-16}" width="190" height="30" rx="8" fill="#fff" stroke="#c4560f"/>')
t(cx(22) - 12, ROW['c'] + 5, '← b~d 20·21은 비워 둔다', 14, 'start', c='#c4560f', bold=True)

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

# ---------------- a20 → 점퍼 → STOP 11
wire(f'M{cx(20)},{ROW["a"]} L{cx(20)},245 C{cx(20)},215 {cx(20)+30},212 {cx(20)+60},212 L1090,212 C1140,212 1150,{TERM["11"][1]} {TERM["11"][0]},{TERM["11"][1]}', ORG)
pin(cx(20), ROW['a'])
t(845, 196, '② 수-수 점퍼 반쪽: a20 → STOP 11번', 15, 'start', c='#c4560f', bold=True)

# a20 · a21 라벨 (선 위에 보이도록 마지막에)
for c, x, anc in ((20, cx(20) - 22, 'end'), (21, cx(21) + 22, 'start')):
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
    '• 20·21열 위쪽(a~e)에는 TENS 선(주황)만. 이 선이 우노 핀·GND·레일에 닿으면 안 된다.',
    '• 꼰 부분, 단자, 노출된 구리는 전부 절연테이프. 주황·빨강 선은 USB·IMU 선과 떨어뜨린다.',
    '• 실험자 E-STOP이 없으니 실험자는 노트북 SPACE(전부 정지), 참가자는 STOP 버튼을 쥔다.',
    '• 멀티미터 절연 확인과 1kΩ 벤치 비교 전에는 이 경로를 사람에게 연결하지 않는다.',
    '• CH2는 30열 오른쪽(a50 · a51)에 같은 방법. 참가자 STOP 하나로 끊으려면 NC 접점 하나 더.',
]
for i, s in enumerate(checks):
    t(QX + 24, QY + 60 + i * 21, s, 14, 'start', c='#c0392b' if i == 3 else '#222', bold=i == 3)

a('</svg>')
svg = os.path.join(HERE, '..', 'docs', 'output_wiring_simple.svg')
io.open(svg, 'w', encoding='utf-8').write('\n'.join(o))
print('ok', os.path.abspath(svg))
