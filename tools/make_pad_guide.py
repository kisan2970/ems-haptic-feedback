"""전극 패드 부착 위치 안내 그림 (손목 신전근 CH1 + 삼두근 CH2)."""
import io, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1500, 1080
F = 'font-family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"'
o = []
def a(s): o.append(s)
def t(x, y, s, size=16, anchor='middle', c='#222', bold=False):
    b = 'font-weight="700"' if bold else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {b}>{s}</text>')
SKIN, SKIN_D = '#f3d3bb', '#c99a7a'

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><filter id="sh"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.22"/></filter>'
  '<marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker>'
  '<marker id="ag" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1d6b35"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="#f2efe8"/>')
t(40, 50, '전극 패드 붙이는 위치 — CH1 손목 신전근', 28, 'start', bold=True)
t(40, 82, '오른팔을 손등이 위로 오게 책상에 올리고 위에서 내려다본 모습 (왼팔이면 좌우만 뒤집기). 1cm = 22px', 15, 'start', c='#555')

# ---------------- main forearm (dorsal view)
S = 22             # px per cm
EX, CY = 160, 340  # lateral epicondyle x, centerline y
WX = EX + 25 * S   # wrist
def half(x):       # half width along forearm
    f = (x - EX) / (WX - EX)
    return 112 - 52 * max(0, min(1, f))
pts_top = [(x, CY - half(x)) for x in range(EX - 120, WX + 1, 10)]
pts_bot = [(x, CY + half(x)) for x in range(WX, EX - 121, -10)]
# upper arm stub
a(f'<path d="M{EX-120},{CY-112} L60,{CY-125} L60,{CY+125} L{EX-120},{CY+112} Z" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>')
path = 'M' + ' L'.join(f'{x},{y}' for x, y in pts_top + pts_bot) + ' Z'
a(f'<path d="{path}" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5" filter="url(#sh)"/>')
# hand (palm down), thumb on top
hx = WX
a(f'<path d="M{hx},{CY-60} C{hx+60},{CY-80} {hx+150},{CY-75} {hx+175},{CY-55} L{hx+250},{CY-58} Q{hx+262},{CY-46} {hx+250},{CY-34} '
  f'L{hx+185},{CY-30} L{hx+262},{CY-22} Q{hx+272},{CY-8} {hx+260},{CY+4} L{hx+185},{CY+2} L{hx+255},{CY+14} Q{hx+264},{CY+28} {hx+252},{CY+38} '
  f'L{hx+180},{CY+34} L{hx+238},{CY+46} Q{hx+246},{CY+60} {hx+232},{CY+66} L{hx+150},{CY+62} C{hx+90},{CY+70} {hx+40},{CY+64} {hx},{CY+58} Z" '
  f'fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/>')
a(f'<path d="M{hx+40},{CY-58} C{hx+80},{CY-110} {hx+130},{CY-128} {hx+165},{CY-118} Q{hx+178},{CY-104} {hx+160},{CY-94} C{hx+130},{CY-90} {hx+100},{CY-72} {hx+80},{CY-60}" '
  f'fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/>')
t(hx + 150, CY - 132, '엄지', 15, c='#7a4d2c', bold=True)
t(hx + 130, CY + 100, '손등', 15, c='#7a4d2c')
# side labels
t(WX + 10, CY - half(WX) - 44, '엄지 쪽 (요측)', 15, 'end', c='#7a4d2c', bold=True)
t(WX - 40, CY + half(WX - 40) + 30, '새끼손가락 쪽 (척측)', 15, 'end', c='#7a4d2c', bold=True)
t(60, CY - 140, '위팔', 14, 'start', c='#7a4d2c')
# muscles (translucent)
def band(x1, x2, yc1, yc2, w, col):
    a(f'<path d="M{x1},{yc1-w} Q{(x1+x2)/2},{(yc1+yc2)/2-w-6} {x2},{yc2-w*0.5} L{x2},{yc2+w*0.5} Q{(x1+x2)/2},{(yc1+yc2)/2+w+6} {x1},{yc1+w} Z" fill="{col}" />')
band(EX - 10, EX + 17 * S, CY - 62, CY - 40, 42, '#e74c3c40')
band(EX + 10, EX + 21 * S, CY + 18, CY + 10, 26, '#3a7bd540')
t(EX + 15 * S, CY + 62, '손가락 폄근 (여기만 자극되면 손가락이 펴짐)', 13, c='#2a5a9e', bold=True)
# epicondyle
a(f'<circle cx="{EX}" cy="{CY-92}" r="15" fill="#e8d8c6" stroke="#8a6a4a" stroke-width="3"/>')
a(f'<line x1="{EX}" y1="{CY-108}" x2="{EX-20}" y2="{CY-170}" stroke="#8a6a4a" stroke-width="2"/>')
t(EX - 22, CY - 194, '팔꿈치 바깥쪽 튀어나온 뼈', 15, c='#5a3a1a', bold=True)
t(EX - 22, CY - 175, '(외측상과) = 기준점', 13, c='#5a3a1a')
# pads 6 x 4 cm, centers at 5.5 cm and 13.5 cm
def pad(cxp, cyp, lab, sub):
    w, h = 6 * S, 4 * S
    a(f'<rect x="{cxp-w/2}" y="{cyp-h/2}" width="{w}" height="{h}" rx="12" fill="#ffffffcc" stroke="#44617e" stroke-width="3" filter="url(#sh)"/>')
    a(f'<rect x="{cxp-w/2+8}" y="{cyp-h/2+8}" width="{w-16}" height="{h-16}" rx="8" fill="#8fa7bf88"/>')
    t(cxp, cyp + 2, lab, 22, c='#1e3a56', bold=True)
    t(cxp, cyp + 24, sub, 12, c='#1e3a56')
PA = (EX + 5.5 * S, CY - 52); PB = (EX + 13.5 * S, CY - 44)
pad(*PA, '패드 A', '(근위)')
pad(*PB, '패드 B', '(원위)')
t(PB[0] + 76, CY - 66, '← 손목 신전근', 15, 'start', c='#a93226', bold=True)
t(PB[0] + 76, CY - 46, '    여기를 자극', 14, 'start', c='#a93226', bold=True)
# lead wires
a(f'<path d="M{PA[0]+20},{PA[1]-44} C{PA[0]+20},{PA[1]-120} {PA[0]+90},{142} {PA[0]+170},{142}" fill="none" stroke="#d62728" stroke-width="5"/>')
a(f'<path d="M{PB[0]+20},{PB[1]-44} C{PB[0]+20},{PB[1]-100} {PB[0]+80},{190} {PB[0]+150},{190}" fill="none" stroke="#222" stroke-width="5"/>')
t(PA[0] + 178, 147, '← 참가자 STOP 12번에서 오는 선 (빨강)', 13, 'start', c='#b02020', bold=True)
t(PB[0] + 158, 195, '← 리드 B (검정)', 13, 'start', c='#222', bold=True)
# dimension lines
yd = CY + 150
def dim(x1, x2, y, lab):
    a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#1d6b35" stroke-width="2" marker-start="url(#ag)" marker-end="url(#ag)"/>')
    a(f'<line x1="{x1}" y1="{y-10}" x2="{x1}" y2="{y+10}" stroke="#1d6b35" stroke-width="2"/><line x1="{x2}" y1="{y-10}" x2="{x2}" y2="{y+10}" stroke="#1d6b35" stroke-width="2"/>')
    t((x1 + x2) / 2, y - 8, lab, 14, c='#1d6b35', bold=True)
dim(EX, PA[0], yd, '패드 A 중심까지 약 5~6cm')
dim(PA[0] + 3 * S, PB[0] - 3 * S, yd + 46, '패드 사이 2cm 이상')
dim(PA[0], PB[0], yd + 92, '중심 사이 약 8cm')
for x in (EX, PA[0], PB[0]):
    a(f'<line x1="{x}" y1="{CY - 20}" x2="{x}" y2="{yd + 92}" stroke="#1d6b35" stroke-width="1" stroke-dasharray="4,4"/>')
t(WX - 20, yd + 40, '손목까지 약 25cm', 13, 'end', c='#777')

# ---------------- side panel: posture + how to find
PX, PY = 1000, 120
a(f'<rect x="{PX}" y="{PY}" width="475" height="430" rx="14" fill="#fff" stroke="#cfc6b4" stroke-width="1.5"/>')
t(PX + 20, PY + 36, '자세 (옆에서 본 모습)', 19, 'start', bold=True)
# table
a(f'<rect x="{PX+30}" y="{PY+170}" width="270" height="16" fill="#b08a5a"/><rect x="{PX+40}" y="{PY+186}" width="14" height="70" fill="#8a6a40"/>')
# arm on table, hand off edge
a(f'<path d="M{PX+40},{PY+150} L{PX+300},{PY+156} L{PX+300},{PY+170} L{PX+40},{PY+170} Z" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>')
a(f'<path d="M{PX+300},{PY+156} Q{PX+350},{PY+158} {PX+380},{PY+178} L{PX+372},{PY+190} Q{PX+340},{PY+176} {PX+300},{PY+170} Z" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>')
a(f'<path d="M{PX+300},{PY+156} Q{PX+350},{PY+138} {PX+382},{PY+112} L{PX+392},{PY+122} Q{PX+355},{PY+152} {PX+300},{PY+170}" fill="none" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="6,4"/>')
a(f'<path d="M{PX+400},{PY+175} Q{PX+425},{PY+140} {PX+402},{PY+110}" fill="none" stroke="#c0392b" stroke-width="3" marker-end="url(#ar)"/>')
t(PX + 420, PY + 100, '자극하면', 13, c='#c0392b', bold=True); t(PX + 420, PY + 84, '손목이 위로', 13, c='#c0392b', bold=True)
a(f'<rect x="{PX+120}" y="{PY+144}" width="40" height="8" rx="2" fill="#8fa7bf"/><rect x="{PX+190}" y="{PY+145}" width="40" height="8" rx="2" fill="#8fa7bf"/>')
t(PX + 175, PY + 136, '패드는 팔 윗면', 12, c='#44617e', bold=True)
t(PX + 30, PY + 290, '• 손바닥이 아래, 손목부터 끝은 책상 밖으로', 14, 'start')
t(PX + 30, PY + 314, '• 손과 팔에 힘을 빼고 그대로 둔다', 14, 'start')
t(PX + 20, PY + 356, '근육 찾는 법', 17, 'start', bold=True)
t(PX + 30, PY + 382, '주먹을 가볍게 쥐고 손등을 위로 젖히면', 14, 'start')
t(PX + 30, PY + 404, '팔꿈치 아래 엄지 쪽 윗면이 볼록 솟는다 → 그 위', 14, 'start')

# ---------------- bottom: adjust / avoid
BX, BY = 40, 700
a(f'<rect x="{BX}" y="{BY}" width="900" height="350" rx="14" fill="#fff" stroke="#cfc6b4" stroke-width="1.5"/>')
t(BX + 20, BY + 36, '켜 보고 반응에 따라 옮기기 (노브를 0으로 돌린 뒤 옮긴다)', 19, 'start', bold=True)
rows = [('손목이 위로 젖혀짐', '정상. 이 위치를 사진으로 기록', '#1d6b35'),
        ('손가락만 펴짐', '두 패드를 엄지 쪽으로 1cm', '#a93226'),
        ('손목이 새끼손가락 쪽으로 꺾임', '두 패드를 엄지 쪽으로 1cm', '#a93226'),
        ('찌릿하기만 하고 안 움직임', '패드 A를 팔꿈치 쪽으로 1cm, 피부에 물 한 방울', '#a93226'),
        ('한 점만 콕콕 따가움', '패드가 들떴음. 다시 붙이거나 새 패드', '#a93226'),
        ('반응이 약하면', '리드 빨강·검정을 서로 바꿔 꽂아 본다', '#555')]
for i, (k, v, c) in enumerate(rows):
    y = BY + 78 + i * 38
    a(f'<circle cx="{BX+30}" cy="{y-5}" r="5" fill="{c}"/>')
    t(BX + 46, y, k, 15, 'start', c=c, bold=True); t(BX + 330, y, '→ ' + v, 15, 'start')
t(BX + 20, BY + 320, '피할 곳: 팔꿈치 접히는 곳, 뼈 바로 위, 손목 가까운 힘줄 부위, 상처·점 위', 14, 'start', c='#c0392b', bold=True)

# ---------------- CH2 inset (triceps, later)
IX, IY = 1000, 580
a(f'<rect x="{IX}" y="{IY}" width="475" height="470" rx="14" fill="#fff" stroke="#cfc6b4" stroke-width="1.5"/>')
t(IX + 20, IY + 36, '나중에: CH2 삼두근 (위팔 뒤)', 19, 'start', bold=True)
t(IX + 20, IY + 60, '팔을 내린 상태에서 뒤에서 본 모습', 13, 'start', c='#555')
a(f'<path d="M{IX+170},{IY+90} Q{IX+150},{IY+250} {IX+175},{IY+410} L{IX+300},{IY+410} Q{IX+322},{IY+250} {IX+300},{IY+90} Z" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/>')
a(f'<ellipse cx="{IX+236}" cy="{IY+250}" rx="52" ry="130" fill="#e74c3c33"/>')
t(IX + 236, IY + 82, '어깨', 13, c='#7a4d2c'); t(IX + 236, IY + 432, '팔꿈치', 13, c='#7a4d2c')
for yy, lab in ((IY + 175, 'A'), (IY + 320, 'B')):
    a(f'<rect x="{IX+213}" y="{yy-56}" width="46" height="112" rx="10" fill="#ffffffcc" stroke="#44617e" stroke-width="3"/>')
    a(f'<rect x="{IX+219}" y="{yy-50}" width="34" height="100" rx="7" fill="#8fa7bf88"/>')
    t(IX + 236, yy + 7, lab, 20, c='#1e3a56', bold=True)
t(IX + 330, IY + 180, '5×10cm 패드 2장', 14, 'start', bold=True)
t(IX + 330, IY + 204, '근육 결 따라 세로로', 13, 'start')
t(IX + 330, IY + 250, '패드 사이 2~3cm', 13, 'start')
t(IX + 330, IY + 296, '팔꿈치에서 손 한 뼘', 13, 'start'); t(IX + 330, IY + 316, '위까지가 근육 중심', 13, 'start')
t(IX + 20, IY + 455, '팔꿈치를 펴며 힘주면 위팔 뒤가 단단해지는 곳', 13, 'start', c='#555')

a('</svg>')
io.open(os.path.join(HERE, '..', 'docs', 'pad_placement.svg'), 'w', encoding='utf-8').write('\n'.join(o))
print('ok')
