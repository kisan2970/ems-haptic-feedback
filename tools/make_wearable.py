"""착용 배치 구상도: 팔에는 패드·IMU·선만 두고, 회로는 책상 박스에 둔다 (구상안).
출력: docs/wearable_layout.svg  (PNG는 브라우저로 렌더)
"""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1900, 1260
F = 'font-family="Malgun Gothic, Apple SD Gothic Neo, WenQuanYi Zen Hei, sans-serif"'
o = []
def a(s): o.append(s)
def t(x, y, s, size=14, anchor='middle', c='#222', bold=False):
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {"font-weight=" + chr(34) + "700" + chr(34) if bold else ""}>{s}</text>')
def tag(x, y, s, size=13, c='#222', anchor='middle'):
    w = sum(1.0 if ord(ch) > 0x2e80 else 0.58 for ch in s) * size + 16
    x0 = x - w / 2 if anchor == 'middle' else x - 8 if anchor == 'start' else x - w + 8
    a(f'<rect x="{x0}" y="{y-size-4}" width="{w}" height="{size+11}" rx="6" fill="#fffdf5" stroke="{c}" stroke-width="1.3" opacity="0.97"/>')
    t(x, y, s, size, anchor, c, True)
def wire(d, col, w=6, dash=None):
    a(f'<path d="{d}" fill="none" stroke="#00000040" stroke-width="{w+3}" stroke-linecap="round"/>')
    a(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" {"stroke-dasharray=" + chr(34) + dash + chr(34) if dash else ""}/>')
def box(x, y, w, h, title, sub='', fill='#fff', stroke='#888'):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2" filter="url(#sh)"/>')
    t(x + w / 2, y + 30, title, 15, bold=True)
    for i, s in enumerate(sub.split('|') if sub else []): t(x + w / 2, y + 54 + i * 20, s, 12, c='#555')

OR1, OR2, IMUc, STOPc, GRY = '#ee7a1d', '#b5530f', '#7d3cc8', '#1d8348', '#7f8c8d'
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.25"/></filter></defs>')
a(f'<rect width="{W}" height="{H}" fill="#e9e6df"/>')
t(40, 48, '착용 배치 구상도 — 팔에는 패드 · IMU · 선만, 회로는 책상 박스에 (구상안)', 26, 'start', bold=True)
t(40, 76, '팔이 자유롭게 움직이도록 무게는 책상에 두고, 선은 한 다발로 어깨 → 등 → 허리로 내린다. 실물 확인 전.', 14, 'start', c='#555')

# ---------------- 사람 (위에서 본 오른팔을 옆으로 뻗은 모습)
SK, SKs = '#f1c9a5', '#c99a74'
a(f'<circle cx="205" cy="190" r="58" fill="{SK}" stroke="{SKs}" stroke-width="3"/>')
a('<rect x="90" y="262" width="250" height="470" rx="46" fill="#cfd6dc" stroke="#9aa5ad" stroke-width="3"/>')
t(215, 520, '몸통', 15, c='#6b7780', bold=True)
a(f'<rect x="318" y="268" width="450" height="96" rx="44" fill="{SK}" stroke="{SKs}" stroke-width="3"/>')      # 위팔
a(f'<rect x="740" y="276" width="420" height="80" rx="38" fill="{SK}" stroke="{SKs}" stroke-width="3"/>')      # 전완
a(f'<ellipse cx="1215" cy="316" rx="72" ry="46" fill="{SK}" stroke="{SKs}" stroke-width="3"/>')               # 손
t(540, 258, '위팔', 13, c='#8a5a3a', bold=True); t(950, 266, '전완', 13, c='#8a5a3a', bold=True); t(1236, 322, '손등', 12, c='#8a5a3a', bold=True)
# 반대쪽 팔과 STOP
a(f'<rect x="52" y="300" width="70" height="330" rx="34" fill="{SK}" stroke="{SKs}" stroke-width="3"/>')
a(f'<ellipse cx="88" cy="660" rx="40" ry="34" fill="{SK}" stroke="{SKs}" stroke-width="3"/>')
a('<rect x="60" y="640" width="56" height="40" rx="8" fill="#2b2b2b"/><circle cx="88" cy="660" r="13" fill="#27ae60" stroke="#145a32" stroke-width="2"/>')

# 패드와 토시
def pad(x, y, w, h, lab):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#9fd3f2" stroke="#2c7fb8" stroke-width="2.5"/>')
    t(x + w / 2, y + h / 2 + 5, lab, 12, c='#1d5a85', bold=True)
pad(470, 300, 96, 50, 'CH2 A'); pad(610, 300, 96, 50, 'CH2 B')
pad(812, 284, 86, 44, 'CH1 A'); pad(940, 284, 86, 44, 'CH1 B')
a('<rect x="792" y="272" width="258" height="88" rx="30" fill="#34495e22" stroke="#34495e" stroke-width="2" stroke-dasharray="8,5"/>')
tag(921, 392, '토시(압박 슬리브)로 패드와 선을 덮는다', 13, '#34495e')
tag(588, 392, 'CH2 패드: 위팔 뒤 (삼두근)', 12.5, '#1d5a85')
# 밴드 (케이블 고정)
for x, lab, ty in ((372, '① 위팔 밴드', 232), (1100, '② 손목 밴드', 240)):
    a(f'<rect x="{x}" y="{260 if x < 500 else 270}" width="26" height="{112 if x < 500 else 92}" rx="8" fill="#34495e"/>')
    tag(x + 13, ty, lab + ': 선 고정', 13, '#34495e')
# IMU
a('<rect x="1176" y="292" width="62" height="42" rx="6" fill="#5b2d8a" stroke="#3a1a5e" stroke-width="2"/>')
t(1207, 318, 'IMU', 12, c='#fff', bold=True)
tag(1200, 400, 'IMU: 열수축 튜브로 감싸 절연', 13, IMUc)

# ---------------- 팔 위의 선
# IMU 선: 팔 위쪽(등쪽) 가장자리
wire('M1176,300 C1150,282 1130,274 1113,274 L790,274 C770,274 770,244 752,244 C734,244 734,270 716,270 L400,270 C350,270 344,262 340,300 L340,700', IMUc, 5)
tag(752, 222, '팔꿈치 여유 고리 5cm', 12.5, IMUc)
# 전극선: 팔 아래쪽 가장자리 (IMU 선과 반대편)
wire('M855,328 L855,352 L983,352', OR1, 5); wire('M983,328 L983,352', OR1, 5)
wire('M855,352 C800,356 780,366 740,366 L420,366 C370,366 358,372 356,410 L356,700', OR1, 6)
wire('M518,350 L518,372 M658,350 L658,372 M658,372 L518,372 C440,376 372,380 372,420 L372,700', OR2, 6)
tag(600, 440, '전극선(주황)은 팔 아래쪽, IMU 선(보라)은 위쪽 — 서로 묶지 않는다', 13, '#a84a08')
t(300, 560, '어깨 → 등 뒤', 12.5, 'end', c='#555', bold=True)
a('<rect x="322" y="690" width="68" height="26" rx="8" fill="#34495e"/>'); tag(408, 709, '③ 허리 클립', 13, '#34495e', 'start')

# ---------------- 책상 박스
BX, BY, BW, BH = 470, 800, 1010, 330
a(f'<rect x="{BX}" y="{BY}" width="{BW}" height="{BH}" rx="18" fill="#f7f5ef" stroke="#8a8473" stroke-width="2.5" stroke-dasharray="10,6"/>')
t(BX + 20, BY + 30, '책상 박스 — 몸에 달지 않는다', 16, 'start', bold=True)
box(BX + 24, BY + 60, 190, 150, 'TENS 7000', '9V 건전지|노브 스토퍼', '#fff')
box(BX + 250, BY + 60, 250, 150, '만능기판 (출력부)', '게이팅 · 강도 사다리|단자대 IN / OUT / 중계', '#f3dcb8', '#8a6d3b')
box(BX + 536, BY + 60, 230, 150, '브레드보드', '555 감시 · 트랜지스터|(저전압만)', '#fff')
box(BX + 802, BY + 60, 180, 150, '우노', 'COM17|USB → 노트북', '#d7e9f5', '#1e74a8')
wire(f'M{BX+214},{BY+120} L{BX+250},{BY+120}', OR1, 5); t(BX + 232, BY + 108, '리드 A', 10.5, c='#a84a08', bold=True)
wire(f'M{BX+500},{BY+135} L{BX+536},{BY+135}', '#8e44ad', 5); t(BX + 518, BY + 123, 'H1', 10.5, c='#6c3483', bold=True)
wire(f'M{BX+802},{BY+110} L{BX+766},{BY+110}', '#2f6fd6', 5)
wire(f'M{BX+892},{BY+210} L{BX+892},{BY+250} L{BX+375},{BY+250} L{BX+375},{BY+210}', '#17a2b8', 5); t(BX + 640, BY + 242, 'H2: 우노 → 만능기판 (강도 사다리)', 11, c='#0b5563', bold=True)
wire(f'M{BX+892},{BY+250} L{BX+892},{BY+290} L{BX+60},{BY+290}', IMUc, 4); t(BX + 480, BY + 308, 'IMU 선 4가닥 → 우노 3.3V · GND · A4 · A5', 11, c=IMUc, bold=True)
# 노트북
box(1560, BY + 60, 290, 150, '노트북 (Processing)', '배터리로 구동|어댑터를 꽂으면 USB 아이솔레이터', '#fff')
wire(f'M{BX+982},{BY+135} L1560,{BY+135}', '#555', 6); t(1520, BY + 122, 'USB', 11, c='#333', bold=True)
# 다발: 허리 클립 → 박스
wire(f'M340,716 C340,790 400,{BY+290} {BX+60},{BY+290}', IMUc, 4)
wire(f'M356,716 C356,800 420,{BY+180} {BX+250},{BY+180}', OR1, 5)
wire(f'M372,716 C372,780 430,{BY+196} {BX+250},{BY+196}', OR2, 5)
wire(f'M88,694 C88,900 300,{BY+160} {BX+250},{BY+160}', STOPc, 5)
tag(250, 880, '선 다발 1.2~1.5m', 13, '#555')
tag(120, 730, '참가자 STOP: 반대쪽 손', 13, STOPc)
t(BX + 262, BY + 164, 'STOP', 10, 'start', c='#fff', bold=True)

# ---------------- 오른쪽 설명
PX, PY = 1330, 110
a(f'<rect x="{PX}" y="{PY}" width="530" height="640" rx="12" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
rows = [('몸에 다는 것 (합쳐서 수십 g)', '#222', True),
        ('· 패드 4장 + 토시, IMU 1개, 밴드 2개, 선', '#333', False),
        ('· 참가자 STOP은 반대쪽 손에 쥔다', '#333', False),
        ('', '', False),
        ('선 다발 (팔 ↔ 박스)', '#222', True),
        ('· 전극선 4가닥: CH1 A·B, CH2 A·B. 채널별로 꼰다', '#a84a08', True),
        ('· IMU 4가닥: SDA+GND, SCL+3.3V로 둘씩 꼰다', IMUc, True),
        ('· STOP 4가닥 (NC 접점 2개): 따로 박스로', STOPc, True),
        ('· 전극선과 IMU 선은 팔의 반대편으로, 묶지 않는다', '#333', False),
        ('', '', False),
        ('움직이기 편하게', '#222', True),
        ('· 선은 밴드 2곳에 고정 → 당겨도 패드·IMU가 안 뜬다', '#333', False),
        ('· 팔꿈치에 여유 고리 → 굽혔다 펴도 안 당긴다', '#333', False),
        ('· 선은 손 쪽이 아니라 어깨 쪽으로 빠진다', '#333', False),
        ('· 패드는 토시가 눌러 준다 (접촉이 흔들리면 따끔)', '#333', False),
        ('', '', False),
        ('꼭 지킬 것', '#b02a1f', True),
        ('· IMU 맨 기판이 피부에 닿으면 PC와 몸이 이어진다', '#b02a1f', True),
        ('  → 열수축 튜브나 케이스로 감싼다', '#b02a1f', False),
        ('· 전극은 팔에만, 선이 몸통 앞을 가로지르지 않게', '#b02a1f', False),
        ('· STOP 복귀선과 패드선은 만능기판 OUT 단자대의', '#333', False),
        ('  예비 핀 한 구멍에 같이 물린다 (중계점)', '#333', False)]
y = PY + 36
for s, c, b in rows:
    if s: t(PX + 22, y, s, 15 if (b and not s.startswith('·')) else 13, 'start', c, b)
    y += 27 if s else 12

# ---------------- 아래: 확인할 것
a(f'<rect x="40" y="1160" width="{W-80}" height="84" rx="12" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
t(60, 1190, '확인이 필요한 것', 15, 'start', bold=True)
t(210, 1190, '① IMU 선이 1m를 넘으면 I2C 400kHz가 불안할 수 있다 → 100kHz로 낮추고(펌웨어 한 줄) 읽기 오류를 본다.   ② 전극선 연장부는 납땜 후 열수축, 당겨서 확인.', 13, 'start', c='#333')
t(60, 1222, '다음 단계(과목 이후): 우노 + 브레드보드를 ESP32 + 기판 한 장으로 줄이고 무선(BLE)으로 바꾸면 박스를 허리 팩으로 옮길 수 있다. 지금 구조에서 선 다발만 짧아진다.', 13, 'start', c='#1d6b35', bold=True)
a('</svg>')
io.open(os.path.join(HERE, '..', 'docs', 'wearable_layout.svg'), 'w', encoding='utf-8').write('\n'.join(o))
print('ok')
