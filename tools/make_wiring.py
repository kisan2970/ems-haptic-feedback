import io, os
W, H = 1600, 1090
o = []
def a(s): o.append(s)
BLUE = '#1f6fd0'; ORG = '#e0671b'
F = 'font-family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"'

def line(pts, c=BLUE, w=3):
    p = ' '.join(f'{x},{y}' for x, y in pts)
    a(f'<polyline points="{p}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"/>')
def dot(x, y, c=BLUE): a(f'<circle cx="{x}" cy="{y}" r="5" fill="{c}"/>')
def text(x, y, t, size=13, anchor='middle', c='#222', bold=False):
    b = 'font-weight="700"' if bold else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {b}>{t}</text>')
def tag(cx, cy, kind):
    col = '#d62728' if kind == '5V' else '#111'
    a(f'<rect x="{cx-20}" y="{cy-9}" width="40" height="18" rx="4" fill="{col}"/>')
    text(cx, cy + 5, kind, 12, c='#fff', bold=True)
def res_h(x1, x2, y, label, c=BLUE):
    m = (x1 + x2) / 2
    line([(x1, y), (m - 20, y)], c); line([(m + 20, y), (x2, y)], c)
    a(f'<rect x="{m-20}" y="{y-8}" width="40" height="16" fill="#f5deb3" stroke="#8a6d3b" stroke-width="2"/>')
    text(m, y - 14, label, 12)
def res_v(x, y1, y2, label, side='right', c=BLUE):
    m = (y1 + y2) / 2
    line([(x, y1), (x, m - 20)], c); line([(x, m + 20), (x, y2)], c)
    a(f'<rect x="{x-8}" y="{m-20}" width="16" height="40" fill="#f5deb3" stroke="#8a6d3b" stroke-width="2"/>')
    if side == 'right': text(x + 12, m + 4, label, 12, 'start')
    else: text(x - 12, m + 4, label, 12, 'end')
def cap_plates_v(x, ytop):
    a(f'<line x1="{x-12}" y1="{ytop}" x2="{x+12}" y2="{ytop}" stroke="#222" stroke-width="3"/>')
    a(f'<line x1="{x-12}" y1="{ytop+8}" x2="{x+12}" y2="{ytop+8}" stroke="#222" stroke-width="3"/>')
def cap_h(x1, x2, y, label):
    m = (x1 + x2) / 2
    line([(x1, y), (m - 4, y)]); line([(m + 4, y), (x2, y)])
    a(f'<line x1="{m-4}" y1="{y-12}" x2="{m-4}" y2="{y+12}" stroke="#222" stroke-width="3"/>')
    a(f'<line x1="{m+4}" y1="{y-12}" x2="{m+4}" y2="{y+12}" stroke="#222" stroke-width="3"/>')
    text(m, y - 18, label, 12)
def sw(x1, x2, y, closed, label, c=BLUE, sub=None):
    line([(x1, y), (x1 + 11, y)], c); line([(x2 - 11, y), (x2, y)], c)
    a(f'<circle cx="{x1+15}" cy="{y}" r="4" fill="#fff" stroke="#222" stroke-width="2"/>')
    a(f'<circle cx="{x2-15}" cy="{y}" r="4" fill="#fff" stroke="#222" stroke-width="2"/>')
    by = y + 6 if closed else y - 12
    a(f'<line x1="{x1+11}" y1="{by}" x2="{x2-11}" y2="{by}" stroke="#222" stroke-width="3"/>')
    m = (x1 + x2) / 2
    a(f'<line x1="{m}" y1="{by}" x2="{m}" y2="{y-24}" stroke="#222" stroke-width="2"/>')
    a(f'<line x1="{m-10}" y1="{y-24}" x2="{m+10}" y2="{y-24}" stroke="#222" stroke-width="3"/>')
    text(m, y - 32, label, 12)
    if sub: text(m, y + 26, sub, 11, c='#555')

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(W / 2, 42, 'EMS 게이팅 회로 배선도 v2 — CH1 (아두이노 우노) · 총 반동 + 물체 무게', 24, bold=True)

a('<rect x="20" y="70" width="850" height="870" rx="10" fill="#eef4ff" stroke="#9db3d6" stroke-width="2"/>')
text(35, 98, '① 브레드보드 · 저전압(5V) 측', 16, 'start', c='#1d4f91', bold=True)
a('<rect x="890" y="70" width="690" height="870" rx="10" fill="#fff3e6" stroke="#e2b48a" stroke-width="2"/>')
text(905, 98, '③ 만능기판 · TENS 출력 측 (납땜 + KF301 나사 단자대)', 16, 'start', c='#9a4a0c', bold=True)

# UNO
a('<rect x="50" y="110" width="170" height="480" rx="8" fill="#1b6fae"/>')
text(120, 350, 'Arduino', 20, c='#fff', bold=True); text(120, 375, 'UNO R3', 20, c='#fff', bold=True)
pins = [('5V', 135), ('GND', 170), ('D9', 205), ('D2', 260), ('D3', 310), ('D8', 360), ('D4', 410), ('D5', 460), ('A4 SDA', 520), ('A5 SCL', 570)]
for n, y in pins:
    a(f'<circle cx="220" cy="{y}" r="6" fill="#ffd54a" stroke="#222"/>')
    text(208, y + 5, n, 13, 'end', c='#fff', bold=True)
line([(226, 135), (242, 135)], '#d62728'); tag(262, 135, '5V')
line([(226, 170), (242, 170)], '#111'); tag(262, 170, 'GND')
text(290, 157, '→ 브레드보드 +/− 레일', 11, 'start', c='#555')

# D9 keepalive -> Q3 discharges 555 timing cap
line([(226, 205), (290, 205)]); cap_h(290, 320, 205, '100nF'); res_h(320, 400, 205, '1kΩ')
line([(400, 205), (470, 205), (470, 285), (538, 285)])
dot(490, 285); res_v(490, 285, 345, '10kΩ', 'right'); tag(490, 354, 'GND')
text(480, 195, '유지 신호: 자극 중 계속 토글', 11, 'start', c='#555')
a('<circle cx="550" cy="285" r="22" fill="#fff" stroke="#222" stroke-width="2"/>')
a('<line x1="538" y1="270" x2="538" y2="300" stroke="#222" stroke-width="3"/>')
line([(538, 278), (560, 263), (560, 250), (600, 250), (600, 320), (720, 320)])
line([(538, 292), (560, 307)], '#111'); a('<polygon points="560,307 548,305 556,297" fill="#111"/>')
line([(560, 307), (560, 330)], '#111'); tag(560, 339, 'GND')
text(485, 243, 'Q3 2N3904', 12, 'start', bold=True)

# panel parts
line([(226, 260), (300, 260)]); sw(300, 370, 260, False, 'E-STOP의 NO 접점'); line([(370, 260), (402, 260)], '#111'); tag(422, 260, 'GND')
line([(226, 310), (300, 310)]); sw(300, 370, 310, False, '키스위치 (ARM)'); line([(370, 310), (402, 310)], '#111'); tag(422, 310, 'GND')
line([(226, 360), (319, 360)])
a('<circle cx="335" cy="360" r="16" fill="#333"/>'); text(335, 365, 'BZ', 11, c='#fff', bold=True)
text(335, 339, '부저 (+ → D8)', 12)
line([(351, 360), (402, 360)], '#111'); tag(422, 360, 'GND')

# D4 trigger path
line([(226, 410), (450, 410)]); cap_h(450, 480, 410, '10nF')
line([(480, 410), (560, 410), (560, 540), (670, 540), (670, 482)])
dot(560, 540); res_v(560, 540, 622, '10kΩ 풀업', 'left'); tag(560, 631, '5V')
text(300, 440, '트리거: 평소 HIGH, 자극 시작 때 0.1ms LOW', 11, 'start', c='#555')

# 555 (top view rotated: pin1 bottom-left, notch left)
cx = [620, 670, 720, 770]
a('<rect x="600" y="380" width="190" height="80" rx="6" fill="#222"/>')
a('<path d="M600,410 a10,10 0 0 1 0,20" fill="#666"/>')
text(695, 425, 'TLC555CP', 15, c='#fff', bold=True)
for x, n, nm in zip(cx, '1234', ['GND', 'TRIG', 'OUT', 'RST']):
    a(f'<rect x="{x-4}" y="460" width="8" height="22" fill="#bbb"/>'); text(x, 453, f'{n} {nm}', 9, c='#ddd')
for x, n, nm in zip(cx, '8765', ['VCC', 'DIS', 'THR', 'CV']):
    a(f'<rect x="{x-4}" y="358" width="8" height="22" fill="#bbb"/>'); text(x, 396, f'{n} {nm}', 9, c='#ddd')
line([(620, 358), (620, 350)], '#d62728'); tag(620, 341, '5V')
line([(670, 358), (670, 320)]); line([(720, 358), (720, 320)]); dot(670, 320); dot(720, 320)
res_v(670, 320, 240, '100kΩ', 'left'); tag(670, 231, '5V')
line([(720, 320), (720, 300)]); cap_plates_v(720, 292); line([(720, 292), (720, 272)], '#111')
tag(720, 263, 'GND'); text(708, 304, '1µF', 12, 'end')
line([(770, 358), (770, 330)]); cap_plates_v(770, 322); line([(770, 322), (770, 300)], '#111')
tag(770, 291, 'GND'); text(786, 334, '10nF', 12, 'start')
text(700, 178, '100kΩ × 1µF = 0.11초: 유지 신호가 끊기면 555가 SSR을 끈다', 11, c='#555')
line([(620, 482), (620, 500)], '#111'); tag(620, 509, 'GND')
line([(770, 482), (770, 500)], '#d62728'); tag(770, 509, '5V')
line([(720, 482), (720, 580), (830, 580)]); res_h(830, 880, 580, '330Ω'); line([(880, 580), (920, 580)])

# D5 gate path
line([(226, 460), (290, 460), (290, 700), (700, 700)]); dot(620, 700)
res_v(620, 700, 770, '10kΩ 풀다운 (필수)', 'left'); tag(620, 779, 'GND')
res_h(700, 760, 700, '1kΩ'); line([(760, 700), (840, 700)])
a('<circle cx="852" cy="700" r="24" fill="#fff" stroke="#222" stroke-width="2"/>')
a('<line x1="840" y1="684" x2="840" y2="716" stroke="#222" stroke-width="3"/>')
line([(840, 692), (862, 676), (862, 640), (920, 640)])
line([(840, 708), (862, 724)], '#111'); a('<polygon points="862,724 850,722 858,714" fill="#111"/>')
line([(862, 724), (862, 745)], '#111'); tag(862, 754, 'GND')
text(862, 790, 'Q1 2N3904', 12, bold=True); text(862, 806, '평평한 면 보고 E-B-C', 11, c='#555')
text(440, 690, '게이트: HIGH 동안만 자극', 11, c='#555')

# SSR
a('<rect x="920" y="555" width="80" height="105" rx="5" fill="#2b2b2b"/>')
a('<circle cx="930" cy="566" r="4" fill="#aaa"/>')
text(960, 600, 'AQY', 13, c='#fff', bold=True); text(960, 617, '210EH', 13, c='#fff', bold=True)
text(914, 572, '1 (+)', 11, 'end'); text(914, 656, '2 (−)', 11, 'end')
text(1006, 572, '4', 12, 'start', bold=True); text(1006, 656, '3', 12, 'start', bold=True)
a('<line x1="960" y1="505" x2="960" y2="720" stroke="#d62728" stroke-width="3" stroke-dasharray="8,6"/>')
text(960, 478, '② 절연 경계', 14, c='#d62728', bold=True)
text(960, 496, '좌우 도체 간격 ≥ 6mm', 11, c='#d62728')
text(960, 742, 'PhotoMOS 내부 빛으로만 연결', 11, c='#d62728')
text(905, 520, '점퍼선 2가닥으로', 11, 'end', c='#555'); text(905, 534, '브레드보드와 연결', 11, 'end', c='#555')

# EMS side
line([(1000, 580), (1060, 580)], ORG); sw(1060, 1140, 580, True, '실험자 E-STOP', c=ORG, sub='NC 접점')
line([(1140, 580), (1180, 580)], ORG); sw(1180, 1260, 580, True, '참가자 STOP', c=ORG, sub='NC, 손에 쥠')
line([(1260, 580), (1380, 580)], ORG)
a('<rect x="1060" y="800" width="240" height="110" rx="10" fill="#e9e9e9" stroke="#666" stroke-width="2"/>')
text(1180, 832, 'TENS 7000 (9V 건전지)', 15, bold=True)
text(1180, 856, 'Normal · Width 300µs · 40Hz · 타이머 C', 12, c='#444')
text(1180, 878, 'CH1 잭 (2.5mm) → 리드선', 12, c='#444')
text(1180, 898, 'USB·어댑터 연결 금지', 11, c='#d62728')
line([(1100, 800), (1100, 640), (1000, 640)], ORG)
text(1110, 700, '리드 A: 잘라서', 11, 'start', c='#9a4a0c'); text(1110, 715, 'SSR 3번으로', 11, 'start', c='#9a4a0c')
line([(1260, 800), (1260, 720), (1380, 720)], ORG)
text(1250, 770, '리드 B: 그대로 전극으로', 11, 'end', c='#9a4a0c')
a('<rect x="1360" y="500" width="205" height="300" rx="40" fill="#f4dcc8" stroke="#c79d7e" stroke-width="2"/>')
text(1462, 528, '전완 배측', 14, bold=True); text(1462, 546, '(손목 신전근)', 12, c='#555')
a('<rect x="1380" y="555" width="60" height="50" rx="6" fill="#8fa7bf" stroke="#44617e" stroke-width="2"/>')
a('<rect x="1380" y="695" width="60" height="50" rx="6" fill="#8fa7bf" stroke="#44617e" stroke-width="2"/>')
text(1448, 578, '패드 A', 12, 'start', bold=True); text(1448, 594, '외측상과 원위 5cm', 11, 'start', c='#444')
text(1448, 718, '패드 B', 12, 'start', bold=True); text(1448, 734, 'A에서 원위 6cm', 11, 'start', c='#444')
text(1462, 650, '↑ 근위(팔꿈치)', 11, c='#777'); text(1462, 666, '↓ 원위(손목)', 11, c='#777')

# IMU
a('<rect x="50" y="660" width="170" height="170" rx="8" fill="#6a3d9a"/>')
text(120, 735, 'MPU-6050', 16, c='#fff', bold=True); text(120, 757, '(GY-521)', 13, c='#fff')
for n, y in [('SCL', 690), ('SDA', 725), ('VCC', 760), ('GND', 795)]:
    a(f'<circle cx="220" cy="{y}" r="6" fill="#ffd54a" stroke="#222"/>'); text(208, y + 5, n, 12, 'end', c='#fff', bold=True)
line([(226, 570), (250, 570), (250, 690), (226, 690)])
line([(226, 520), (265, 520), (265, 725), (226, 725)])
line([(226, 760), (242, 760)], '#d62728'); tag(262, 760, '5V')
line([(226, 795), (242, 795)], '#111'); tag(262, 795, 'GND')
text(135, 852, '손등에 벨크로 고정', 11, c='#555')

a('<rect x="300" y="830" width="555" height="98" rx="8" fill="#ffffff" stroke="#9db3d6"/>')
notes = ['• 모든 5V / GND 태그는 브레드보드 +/− 레일에 꽂는다 (우노 5V·GND → 레일 한 번만).',
         '• CH2(삼두근): 같은 회로 한 벌 더 — 트리거 D7, 게이트 D6, 유지 신호 D10.',
         '• 첫 테스트는 SSR 3·4번에 TENS 대신 건전지 + LED + 1kΩ을 걸어 깜빡임만 본다.',
         '• 555는 D9가 토글되는 동안만 켜짐. 아두이노가 멈추면 0.11초 안에 차단.']
for i, t in enumerate(notes): text(312, 855 + i * 21, t, 12, 'start')

ly = 975
text(30, ly, '범례', 14, 'start', bold=True)
line([(80, ly - 5), (120, ly - 5)]); text(128, ly, '저전압 신호선', 13, 'start')
line([(260, ly - 5), (300, ly - 5)], ORG); text(308, ly, 'TENS 출력선 (사람에게 가는 선, 아두이노와 절대 연결 금지)', 13, 'start')
tag(760, ly - 5, '5V'); text(786, ly, '5V 레일', 13, 'start'); tag(880, ly - 5, 'GND'); text(906, ly, 'GND 레일', 13, 'start')
dot(1010, ly - 5); text(1022, ly, '연결점 (점 없는 교차는 연결 아님)', 13, 'start')
text(30, ly + 32, '실험자 E-STOP은 버튼 하나에 NC 접점(전극 경로 차단)과 NO 접점(D2로 펌웨어 통보)이 함께 있는 1NC+1NO 제품. 두 STOP 모두 전극 경로에 직렬이라 펌웨어와 무관하게 전류를 끊는다.', 12, 'start', c='#444')
text(30, ly + 54, '전극은 팔에만. 가슴·목·머리 금지, 양팔에 걸친 배치 금지. 사람 연결은 GUIDE.md 5단계 벤치 테스트와 안전장치 8종 검사 통과 후.', 12, 'start', c='#d62728', bold=True)
a('</svg>')
io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'wiring_ch1_uno.svg'), 'w', encoding='utf-8').write('\n'.join(o))
print('ok')
