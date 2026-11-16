"""만능기판(7x9cm) 출력부 실물 배치도 + 꽂는 위치 목록 생성 (구상안).
기판에는 TENS 쪽(게이팅 PhotoMOS, 강도 사다리, 단자대)만 올리고, 555 감시 회로는 브레드보드에 둔다.
출력: docs/perfboard_7x9.svg, docs/PERFBOARD.md  (PNG는 브라우저로 렌더)
구멍 표기: (열, 행). 부품면에서 내려다보고 왼쪽 위 구멍이 (1, 1). 30열 x 24행을 쓴다.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, '..', 'docs')
W, Hh = 1990, 1430
P = 36
X0, Y0 = 420, 230
COLS, ROWS = 30, 24
F = 'font-family="Malgun Gothic, Apple SD Gothic Neo, WenQuanYi Zen Hei, sans-serif"'

o, top = [], []          # o: 기판·배선, top: 부품(배선 위에 그림)
used = {}                # (열,행) -> 무엇이 꽂히는지
md_parts, md_wires = [], []

def a(s): o.append(s)
def b(s): top.append(s)
def H(c, r): return (X0 + (c - 1) * P, Y0 + (r - 1) * P)
def text(x, y, s, size=13, anchor='middle', c='#222', bold=False, dst=None):
    w = 'font-weight="700"' if bold else ''
    (dst if dst is not None else o).append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}" {F} {w}>{s}</text>')
def tag(x, y, s, size, c, dst, fill='#fffdf5', stroke=None):
    """배경이 있는 이름표 (구멍·배선 위에서도 읽히게)."""
    w = sum(1.0 if ord(ch) > 0x2e80 else 0.58 for ch in s) * size + 14
    dst.append(f'<rect x="{x-w/2}" y="{y-size-3}" width="{w}" height="{size+10}" rx="5" fill="{fill}" stroke="{stroke or c}" stroke-width="1.2" opacity="0.96"/>')
    text(x, y, s, size, c=c, bold=True, dst=dst)
def use(c, r, what):
    assert 1 <= c <= COLS and 1 <= r <= ROWS, (c, r)
    assert (c, r) not in used, f'구멍 중복 ({c},{r}): {used[(c, r)]} / {what}'
    used[(c, r)] = what
def hs(c, r): return f'({c},{r})'

OR1, OR2 = '#ee7a1d', '#b5530f'
PUR, BLU, TEAL, BLK = '#8e44ad', '#2f6fd6', '#17a2b8', '#222'
net_pts = {}             # 배선이 지나는 구멍 -> 넷 이름 (서로 다른 넷이 같은 구멍을 쓰면 오류)

def trace(pts, col, net, what=None):
    """뒷면 배선. pts는 구멍 좌표 목록 (직각으로만 꺾는다)."""
    for (c1, r1), (c2, r2) in zip(pts, pts[1:]):
        assert c1 == c2 or r1 == r2, (pts, '직각 아님')
        rng = [(c1, r) for r in range(min(r1, r2), max(r1, r2) + 1)] if c1 == c2 else [(c, r1) for c in range(min(c1, c2), max(c1, c2) + 1)]
        for h in rng:
            assert net_pts.get(h, net) == net, f'배선 충돌 {h}: {net_pts[h]} / {net}'
            net_pts[h] = net
    d = 'M' + ' L'.join(f'{H(c, r)[0]},{H(c, r)[1]}' for c, r in pts)
    a(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" opacity="0.92"/>')
    if what: md_wires.append((net, what, ' → '.join(hs(c, r) for c, r in pts)))

def resistor(c1, c2, r, val, net1, net2, name):
    use(c1, r, name); use(c2, r, name)
    for (c, n) in ((c1, net1), (c2, net2)):
        assert net_pts.get((c, r), n) == n, f'저항 다리 충돌 ({c},{r})'
        net_pts[(c, r)] = n
    for c in range(min(c1, c2) + 1, max(c1, c2)):        # 몸통 아래 구멍에는 같은 행 방향 배선이 없어야 한다
        pass
    (x1, y), (x2, _) = H(c1, r), H(c2, r)
    mx = (x1 + x2) / 2
    b(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#a9a9a9" stroke-width="3.2"/>')
    b(f'<rect x="{mx-34}" y="{y-10}" width="68" height="20" rx="9" fill="#8ec2e6" stroke="#4f7fa3" stroke-width="1.4"/>')
    text(mx, y + 4.5, val, 11.5, c='#12324a', bold=True, dst=top)
    for x in (x1, x2): b(f'<circle cx="{x}" cy="{y}" r="5.2" fill="#d9d9d9" stroke="#666" stroke-width="1.2"/>')
    md_parts.append((name, f'{hs(c1, r)} ↔ {hs(c2, r)}'))

def chip(c, r_top, name, rotated, nets):
    """DIP-4 AQY210EH. rotated=False: 위 4·3, 아래 1·2 (홈 왼쪽). True: 위 2·1, 아래 3·4 (홈 오른쪽)."""
    r_bot = r_top + 3
    pins = {(c, r_top): '2' if rotated else '4', (c + 1, r_top): '1' if rotated else '3',
            (c, r_bot): '3' if rotated else '1', (c + 1, r_bot): '4' if rotated else '2'}
    for (pc, pr), n in pins.items():
        use(pc, pr, f'{name} {n}번')
        net_pts.setdefault((pc, pr), nets[n])
        assert net_pts[(pc, pr)] == nets[n], f'{name} {n}번 넷 불일치 {net_pts[(pc, pr)]} / {nets[n]}'
    (xl, yt), (xr, yb) = H(c, r_top), H(c + 1, r_bot)
    b(f'<rect x="{xl-15}" y="{yt+9}" width="{xr-xl+30}" height="{yb-yt-18}" rx="5" fill="#1c1c1c" stroke="#000" filter="url(#sh)"/>')
    nx = xr + 15 if rotated else xl - 15
    b(f'<path d="M{nx},{(yt+yb)/2-10} a10,10 0 0 {0 if rotated else 1} 0,20" fill="#555"/>')
    text((xl + xr) / 2, (yt + yb) / 2 - 2, 'AQY', 11, c='#eee', bold=True, dst=top)
    text((xl + xr) / 2, (yt + yb) / 2 + 13, name.split()[-1], 11.5, c='#ffb070', bold=True, dst=top)
    for (pc, pr), n in pins.items():
        x, y = H(pc, pr)
        b(f'<circle cx="{x}" cy="{y}" r="5.4" fill="#d9d9d9" stroke="#555" stroke-width="1.2"/>')
        text(x, y + (22 if pr == r_top else -15), n, 10.5, c='#ffd54a', bold=True, dst=top)
    order = ['4', '3', '1', '2'] if not rotated else ['2', '1', '3', '4']
    locs = [(c, r_top), (c + 1, r_top), (c, r_bot), (c + 1, r_bot)]
    md_parts.append((f'{name} (홈이 {"오른쪽" if rotated else "왼쪽"})', ', '.join(f'{n}번={hs(*l)}' for n, l in zip(order, locs))))

def terminal(c, r, up, labels, name, nets):
    """KF301-2P. 핀은 (c, r)와 (c+2, r). up=True면 전선 구멍이 기판 위쪽 가장자리를 향한다."""
    for i, cc in enumerate((c, c + 2)):
        use(cc, r, f'{name} {labels[i]}')
        if nets[i]:
            assert net_pts.get((cc, r), nets[i]) == nets[i]; net_pts[(cc, r)] = nets[i]
    (x1, y), (x2, _) = H(c, r), H(c + 2, r)
    yt = y - 46 if up else y - 26
    b(f'<rect x="{x1-26}" y="{yt}" width="{x2-x1+52}" height="72" rx="5" fill="#2f9e58" stroke="#1b6b39" stroke-width="2" filter="url(#sh)"/>')
    for i, x in enumerate((x1, x2)):
        b(f'<circle cx="{x}" cy="{y}" r="12" fill="#cfd3d6" stroke="#555" stroke-width="1.5"/><line x1="{x-8}" y1="{y-5}" x2="{x+8}" y2="{y+5}" stroke="#555" stroke-width="3"/>')
        wy = yt + 8 if up else yt + 64
        b(f'<rect x="{x-9}" y="{wy-7}" width="18" height="13" rx="2" fill="#11331f"/>')
        tag(x + (0 if nets[i] else 0), y + (44 if up else -36), labels[i], 11, '#0e3d21' if nets[i] else '#888', top)
    md_parts.append((f'단자대 {name} (KF301-2P)', f'{labels[0]}={hs(c, r)}, {labels[1]}={hs(c + 2, r)}'))

def header(holes, name):
    for (c, r), lab in holes:
        use(c, r, f'{name} {lab}')
        x, y = H(c, r)
        b(f'<rect x="{x-12}" y="{y-12}" width="24" height="24" rx="2" fill="#151515"/><rect x="{x-4.5}" y="{y-4.5}" width="9" height="9" fill="#e0b84a" stroke="#7a5c10"/>')
    md_parts.append((f'핀헤더 {name}', ', '.join(f'{lab}={hs(c, r)}' for (c, r), lab in holes)))

# ------------------------------------------------------------------ 바탕
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">')
a('<defs><filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.28"/></filter>'
  '<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="#d6272833" stroke-width="5"/></pattern></defs>')
a(f'<rect width="{W}" height="{Hh}" fill="#e9e6df"/>')
text(40, 46, '만능기판 실물 배치도 (7×9cm) — 출력부: 게이팅 + 강도 사다리, 2채널 (구상안)', 26, 'start', bold=True)
text(40, 74, '부품면에서 내려다본 모습 · 굵은 색선은 뒷면 배선 · 구멍은 (열, 행), 왼쪽 위가 (1, 1) · 555 감시 회로와 우노는 브레드보드에 그대로', 14, 'start', c='#555')

bx, by = X0 - 34, Y0 - 34
bw, bh = (COLS - 1) * P + 68, (ROWS - 1) * P + 68
a(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="#c9a66b" stroke="#8a6d3b" stroke-width="2" filter="url(#sh)"/>')
# 구역 색
def band(r1, r2, fill, stroke=None):
    y1, y2 = H(1, r1)[1] - P / 2, H(1, r2)[1] + P / 2
    a(f'<rect x="{bx+6}" y="{y1}" width="{bw-12}" height="{y2-y1}" fill="{fill}" {"stroke=" + chr(34) + stroke + chr(34) if stroke else ""}/>')
band(1, 7, '#ff8a3d2e'); band(18, 24, '#b5530f2e'); band(10, 15, '#2f6fd61f')
for r1 in (8, 16):
    y1 = H(1, r1)[1] - P / 2
    a(f'<rect x="{bx+6}" y="{y1}" width="{bw-12}" height="{2*P}" fill="url(#hatch)"/>')
for c in range(1, COLS + 1):
    for r in range(1, ROWS + 1):
        x, y = H(c, r)
        a(f'<circle cx="{x}" cy="{y}" r="6.5" fill="#d9a441" stroke="#9c7420" stroke-width="1"/><circle cx="{x}" cy="{y}" r="2.6" fill="#5a4a2a"/>')
    if c == 1 or c % 5 == 0:
        text(H(c, 1)[0], by - 8, str(c), 12, c='#6b6455', bold=True); text(H(c, 1)[0], by + bh + 18, str(c), 12, c='#6b6455', bold=True)
for r in range(1, ROWS + 1):
    if r == 1 or r % 5 == 0 or r in (7, 8, 9, 16, 17, 18, 24):
        text(bx + bw + 14, H(1, r)[1] + 4, str(r), 11, c='#6b6455', bold=True)
labels = []
tag(H(15, 1)[0], H(1, 2)[1] + 6, 'CH1 · TENS 쪽 (손목 신전근)', 15, '#a84a08', labels)
tag(H(15, 1)[0], H(1, 23)[1] + 6, 'CH2 · TENS 쪽 (삼두근)', 15, '#7d3a0a', labels)
tag(H(28, 1)[0], H(1, 12.5)[1] - 22, '저전압 쪽', 14, '#1f4f9e', labels)
tag(H(28, 1)[0], H(1, 12.5)[1] + 30, '우노 5V·GND', 12, '#1f4f9e', labels)
for r1 in (8, 16):
    tag(H(17.5, 1)[0], H(1, r1 + 0.5)[1] + 5, f'{r1}·{r1+1}행 비움 (절연 경계)', 13, '#b02a1f', labels)
    tag(H(28, 1)[0], H(1, r1 + 0.5)[1] + 5, '납·선 금지', 12, '#b02a1f', labels)

# ------------------------------------------------------------------ 회로 (채널 2개)
GA, LA, LB = 5, 11, 23                       # 칩 왼쪽 다리 열
def channel(n, col):
    top_side = (n == 1)
    R = (lambda r: r) if top_side else (lambda r: 25 - r)      # CH2는 위아래 거울상
    pre = f'CH{n}'
    IN, N0, N1, N2 = f'{pre} IN', f'{pre} N0', f'{pre} N1', f'{pre} N2'
    # 뒷면 배선 (TENS 쪽)
    trace([(GA, R(2)), (GA, R(7))], col, IN, '리드 A 단자 → 게이팅 PhotoMOS')
    trace([(GA + 1, R(7)), (LA, R(7))], col, N0, '게이팅 출력 → LA'); trace([(8, R(7)), (8, R(5))], col, N0, 'R1 왼쪽 다리로')
    trace([(LA + 1, R(7)), (LB, R(7))], col, N1, 'LA → LB (R1과 R2 사이)')
    trace([(13, R(7)), (13, R(5))], col, N1, 'R1 오른쪽 다리로'); trace([(19, R(7)), (19, R(5))], col, N1, 'R2 왼쪽 다리로')
    trace([(LB + 1, R(7)), (25, R(7)), (25, R(2))], col, N2, 'LB → OUT 단자'); trace([(24, R(5)), (25, R(5))], col, N2, 'R2 오른쪽 다리 → OUT 줄')
    resistor(8, 13, R(5), '470Ω', N0, N1, f'{pre} R1 470Ω (사다리)')
    resistor(19, 24, R(5), '1kΩ', N1, N2, f'{pre} R2 1kΩ (사다리)')
    terminal(3, R(2), top_side, ['예비', '리드 A'], f'{pre} IN', [None, IN])
    terminal(25, R(2), top_side, ['OUT→STOP', '예비'], f'{pre} OUT', [N2, None])
    return IN, N0, N1, N2
n1 = channel(1, OR1)
n2 = channel(2, OR2)

# 저전압 쪽 뒷면 배선
G1P, G1M, G2P, G2M = 'G1+', 'G1-', 'G2+', 'G2-'
trace([(5, 10), (5, 11), (2, 11)], PUR, G1P, 'CH1 게이팅 1번 → 헤더 G1+')
trace([(6, 10), (6, 12), (2, 12)], BLU, G1M, 'CH1 게이팅 2번 → 헤더 G1−')
trace([(6, 15), (6, 13), (2, 13)], PUR, G2P, 'CH2 게이팅 1번 → 헤더 G2+')
trace([(5, 15), (5, 14), (2, 14)], BLU, G2M, 'CH2 게이팅 2번 → 헤더 G2−')
trace([(11, 10), (11, 11)], TEAL, 'LA1a', 'CH1 LA 1번 → 330Ω'); trace([(16, 11), (17, 11)], TEAL, 'LA1', '330Ω → 헤더 LA1')
trace([(23, 10), (22, 10)], TEAL, 'LB1a', 'CH1 LB 1번 → 330Ω'); trace([(18, 10), (18, 11)], TEAL, 'LB1', '330Ω → 헤더 LB1')
trace([(12, 15), (13, 15)], TEAL, 'LA2a', 'CH2 LA 1번 → 330Ω'); trace([(17, 15), (17, 14)], TEAL, 'LA2', '330Ω → 헤더 LA2')
trace([(24, 15), (24, 14)], TEAL, 'LB2a', 'CH2 LB 1번 → 330Ω'); trace([(19, 14), (18, 14)], TEAL, 'LB2', '330Ω → 헤더 LB2')
trace([(12, 10), (13, 10), (13, 12), (24, 12), (24, 10)], BLK, 'GND', 'CH1 LA 2번 · LB 2번 → GND 줄 (12행)')
trace([(11, 15), (11, 13), (22, 13), (22, 15), (23, 15)], BLK, 'GND', 'CH2 LA 2번 · LB 2번 → GND 줄 (13행)')
trace([(17, 12), (17, 13)], BLK, 'GND', '12행 GND ↔ 13행 GND'); trace([(18, 12), (18, 13)], BLK, 'GND')
resistor(11, 16, 11, '330Ω', 'LA1a', 'LA1', 'CH1 LA용 330Ω')
resistor(22, 18, 10, '330Ω', 'LB1a', 'LB1', 'CH1 LB용 330Ω')
resistor(13, 17, 15, '330Ω', 'LA2a', 'LA2', 'CH2 LA용 330Ω')
resistor(24, 19, 14, '330Ω', 'LB2a', 'LB2', 'CH2 LB용 330Ω')

# 칩 (절연 경계에 걸친다)
chip(GA, 7, 'CH1 게이팅', False, {'4': n1[0], '3': n1[1], '1': G1P, '2': G1M})
chip(LA, 7, 'CH1 LA', False, {'4': n1[1], '3': n1[2], '1': 'LA1a', '2': 'GND'})
chip(LB, 7, 'CH1 LB', False, {'4': n1[2], '3': n1[3], '1': 'LB1a', '2': 'GND'})
chip(GA, 15, 'CH2 게이팅', True, {'3': n2[0], '4': n2[1], '1': G2P, '2': G2M})
chip(LA, 15, 'CH2 LA', True, {'3': n2[1], '4': n2[2], '1': 'LA2a', '2': 'GND'})
chip(LB, 15, 'CH2 LB', True, {'3': n2[2], '4': n2[3], '1': 'LB2a', '2': 'GND'})

header([((2, 11), 'G1+'), ((2, 12), 'G1−'), ((2, 13), 'G2+'), ((2, 14), 'G2−')], 'H1 (게이팅, 1×4)')
header([((17, 11), 'LA1'), ((18, 11), 'LB1'), ((17, 12), 'GND'), ((18, 12), 'GND'),
        ((17, 13), 'GND'), ((18, 13), 'GND'), ((17, 14), 'LA2'), ((18, 14), 'LB2')], 'H2 (강도 사다리, 2×4)')
for (c, r), lab, dx, anc in [((17, 11), 'LA1', -18, 'end'), ((18, 11), 'LB1', 18, 'start'), ((17, 14), 'LA2', -18, 'end'), ((18, 14), 'LB2', 18, 'start')]:
    x, y = H(c, r)
    b(f'<rect x="{x+dx-(34 if anc=="end" else 0)}" y="{y-9}" width="34" height="17" rx="4" fill="#fff" stroke="#0f6f80"/>')
    text(x + dx + (-17 if anc == 'end' else 17), y + 4, lab, 10.5, c='#0f6f80', bold=True, dst=top)
text(H(17.5, 1)[0] - 0, H(1, 12.5)[1] + 4, 'GND', 10.5, c='#fff', bold=True, dst=top)

# 절연 거리 검사: TENS 쪽과 저전압 쪽 구멍은 3칸(7.62mm) 이상, 두 채널은 서로 더 멀리
hv = {h: n for h, n in net_pts.items() if n.startswith('CH')}
lv = [h for h, n in net_pts.items() if not n.startswith('CH')]
for (c, r) in hv:
    for (c2, r2) in lv:
        assert (c - c2) ** 2 + (r - r2) ** 2 >= 9, f'절연 거리 부족 {(c, r)} ↔ {(c2, r2)}'
assert all(1 <= r <= 7 or 18 <= r <= 24 for (_, r) in hv) and all(10 <= r <= 15 for (_, r) in lv)

# ------------------------------------------------------------------ 바깥 연결
def flex(d, col, w=8):
    top.append(f'<path d="{d}" fill="none" stroke="#00000045" stroke-width="{w+3}" stroke-linecap="round"/>')
    top.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
# TENS
b('<rect x="40" y="130" width="240" height="250" rx="22" fill="#f7f7f5" stroke="#9a9a9a" stroke-width="2" filter="url(#sh)"/>')
b('<rect x="66" y="152" width="188" height="64" rx="6" fill="#b9c7a9" stroke="#666"/>')
text(160, 180, 'TENS 7000', 17, c='#223', bold=True, dst=top); text(160, 202, 'Normal · 300µs · 40Hz', 12, c='#223', dst=top)
for kx, lab in ((110, 'CH1'), (210, 'CH2')):
    b(f'<circle cx="{kx}" cy="270" r="24" fill="#ddd" stroke="#777" stroke-width="2.5"/><circle cx="{kx}" cy="270" r="6" fill="#555"/>')
    text(kx, 318, lab, 13, bold=True, dst=top)
text(160, 350, '9V 건전지 · 노브 스토퍼', 11.5, c='#555', dst=top)
x5, x25 = H(5, 1)[0], H(25, 1)[0]
yt, yb = by - 0, by + bh
flex(f'M280,180 C330,180 330,118 380,118 L{x5-24},118 Q{x5},118 {x5},142 L{x5},{H(1,1)[1]-12}', '#d62728')
text(300, 106, 'CH1 리드 A(빨강) 기기 쪽 반', 12.5, 'start', c='#b02a1f', bold=True, dst=top)
flex(f'M210,380 C210,430 22,400 22,470 L22,{yb+36} Q22,{yb+58} 44,{yb+58} L{x5-22},{yb+58} Q{x5},{yb+58} {x5},{yb+36} L{x5},{H(1,24)[1]+12}', '#a01d1d')
text(52, yb + 50, 'CH2 리드 A(빨강) 기기 쪽 반', 12.5, 'start', c='#7d1515', bold=True, dst=top)
# 참가자 STOP + 패드
SX, SY = 1600, 120
b(f'<rect x="{SX}" y="{SY}" width="300" height="190" rx="14" fill="#2b2b2b" filter="url(#sh)"/>')
b(f'<circle cx="{SX+150}" cy="{SY+62}" r="40" fill="#27ae60" stroke="#145a32" stroke-width="3"/>')
text(SX + 150, SY - 10, '참가자 STOP (NC 접점)', 14, bold=True, dst=top)
T = {}
for nm, tx in (('NC1', SX + 30), ('NC2', SX + 170)):
    b(f'<rect x="{tx}" y="{SY+128}" width="100" height="46" rx="5" fill="#ddd" stroke="#888"/>')
    text(tx + 50, SY + 146, nm + (' · CH1' if nm == 'NC1' else ' · CH2'), 11, c='#c0392b', bold=True, dst=top)
    T[nm] = ((tx + 22, SY + 162), (tx + 78, SY + 162))
    for px, py in T[nm]: b(f'<circle cx="{px}" cy="{py}" r="6" fill="#c9a227" stroke="#7a5c10"/>')
flex(f'M{x25},{H(1,1)[1]-12} L{x25},136 Q{x25},100 {x25+36},100 L1540,100 Q1575,100 1575,140 L1575,{SY+205} Q1575,{SY+222} {T["NC1"][0][0]-14},{SY+222} Q{T["NC1"][0][0]},{SY+222} {T["NC1"][0][0]},{T["NC1"][0][1]}', OR1)
text(x25 + 60, 90, 'CH1 OUT → STOP NC1', 12.5, 'start', c='#a84a08', bold=True, dst=top)
flex(f'M{x25},{H(1,24)[1]+12} L{x25},{yb+36} Q{x25},{yb+58} {x25+22},{yb+58} L1938,{yb+58} Q1962,{yb+58} 1962,{yb+34} L1962,{SY+236} Q1962,{SY+214} 1940,{SY+214} L{T["NC2"][0][0]+14},{SY+214} Q{T["NC2"][0][0]},{SY+214} {T["NC2"][0][0]},{T["NC2"][0][1]}', OR2)
text(x25 + 40, yb + 50, 'CH2 OUT → STOP NC2', 12.5, 'start', c='#7d3a0a', bold=True, dst=top)
for nm, px, lab, col in (('NC1', 1650, 'CH1 패드 A', '#d62728'), ('NC2', 1850, 'CH2 패드 A', '#a01d1d')):
    b(f'<rect x="{px-48}" y="424" width="96" height="62" rx="9" fill="#9fd3f2" stroke="#2c7fb8" stroke-width="2.5"/>')
    text(px, 460, lab, 13, c='#1d5a85', bold=True, dst=top)
    sx, sy = T[nm][1]
    flex(f'M{sx},{sy} C{sx},{sy+70} {px},{360} {px},424', col)
text(1750, 512, '리드 A 패드 쪽 반(빨강): STOP → 패드 A', 12.5, c='#b02a1f', bold=True, dst=top)
text(1750, 532, '리드 B(검정)는 자르지 않고 TENS → 패드 B 그대로', 12.5, c='#333', dst=top)

# 헤더 설명 (왼쪽 H1, 오른쪽 H2)
b('<rect x="40" y="560" width="318" height="186" rx="10" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
text(56, 586, 'H1 ← 브레드보드 (게이팅)', 14, 'start', bold=True, dst=top)
rows1 = [('G1+', 'j20  (CH1 330Ω 뒤, 555 출력)', PUR, 11), ('G1−', 'j21  (CH1 Q1 컬렉터)', BLU, 12),
         ('G2+', 'j50  (CH2 330Ω 뒤)', PUR, 13), ('G2−', 'j51  (CH2 Q2 컬렉터)', BLU, 14)]
for i, (pin, src, col, r) in enumerate(rows1):
    y = 612 + i * 26
    text(56, y, pin, 13, 'start', c=col, bold=True, dst=top); text(100, y, '← ' + src, 12.5, 'start', c='#333', dst=top)
    hx_, hy_ = H(2, r)
    flex(f'M358,{y-5} C{372},{y-5} {372},{hy_} {hx_-12},{hy_}', col, 4)
text(56, 728, '브레드보드의 AQY 칩 자리는 비운다', 12, 'start', c='#b02a1f', bold=True, dst=top)
b('<rect x="1540" y="566" width="400" height="200" rx="10" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
text(1556, 592, 'H2 ← 우노에서 바로 (강도 사다리)', 14, 'start', bold=True, dst=top)
for i, s in enumerate(['LA1 ← D11      LB1 ← D12   (CH1)', 'LA2 ← A0        LB2 ← A1    (CH2)', 'GND ← 우노 GND (가운데 4핀 아무 곳)',
                       '330Ω이 기판에 있어 우노 핀을 바로 꽂아도 된다', '선이 빠지면 가장 약한 단계가 된다']):
    text(1556, 620 + i * 26, s, 12.5, 'start', c='#0f6f80' if i < 3 else '#444', bold=i < 3, dst=top)
hx_, hy_ = H(18, 12.5)
top.append(f'<path d="M{hx_+16},{hy_} L1540,{hy_ + 0}" fill="none" stroke="#0f6f80" stroke-width="2" stroke-dasharray="6,5"/>')

# ------------------------------------------------------------------ 범례 · 순서
LY = yb + 96
a(f'<rect x="40" y="{LY}" width="930" height="{Hh-LY-20}" rx="10" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
text(60, LY + 30, '범례 · 꼭 지킬 것', 17, 'start', bold=True)
lx = 60
for col, t_ in [(OR1, 'CH1 TENS'), (OR2, 'CH2 TENS'), (PUR, '게이팅 +'), (BLU, '게이팅 −'), (TEAL, '사다리 신호'), (BLK, 'GND')]:
    a(f'<line x1="{lx}" y1="{LY+52}" x2="{lx+28}" y2="{LY+52}" stroke="{col}" stroke-width="8" stroke-linecap="round"/>')
    text(lx + 36, LY + 57, t_, 12.5, 'start'); lx += 36 + len(t_) * 11 + 26
for i, s in enumerate([
        '1. 주황 구역(1~7행, 18~24행)은 사람에게 가는 TENS 전류. 파랑 구역(10~15행)은 우노 쪽. 둘은 칩 속의 빛으로만 이어진다.',
        '2. 8·9행과 16·17행에는 아무것도 납땜하지 않는다. 기판이 줄 동박(스트립) 종류면 이 줄의 동박을 칼로 끊는다.',
        '3. CH1 칩은 홈이 왼쪽, CH2 칩은 180° 돌려 홈이 오른쪽. 다리 번호(노란 글자)를 그림과 맞춘다.',
        '4. TENS 쪽 배선은 피복선으로 짧게, 납이 옆 구멍으로 번지지 않게. 저전압 쪽은 납 브리지나 나선으로 된다.',
        '5. 구멍 수는 제품마다 다르다. 가장자리가 아니라 왼쪽 위 구멍을 (1,1)로 잡고 센다.']):
    text(60, LY + 86 + i * 24, s, 12.8, 'start', c='#b02a1f' if i == 1 else '#333', bold=(i == 1))
a(f'<rect x="990" y="{LY}" width="960" height="{Hh-LY-20}" rx="10" fill="#fff" stroke="#bdb6a6" stroke-width="1.5"/>')
text(1010, LY + 30, '납땜 순서와 확인', 17, 'start', bold=True)
for i, s in enumerate([
        '① 부품을 꽂기만 하고 이 그림과 비교 (칩 방향, 저항 값) → 사진',
        '② 저항 6개(CH1만이면 4개) → 칩 → 핀헤더 → 단자대 순서로 납땜',
        '③ 뒷면 배선: 저전압 쪽 먼저, TENS 쪽은 나중에. 끝나면 플럭스 닦기',
        '④ 멀티미터: TENS 쪽 ↔ 저전압 쪽 무한대, CH1 ↔ CH2 무한대, 옆 구멍끼리 단락 없음',
        '⑤ LED 부하로 ssr_blink.py, ladder_test.py → 통과 후 1kΩ 벤치 비교 → 그다음에 사람',
        '사전 조건: 강도 사다리(v2.2)를 브레드보드에서 LED로 먼저 확인한다']):
    text(1010, LY + 62 + i * 25, s, 12.8, 'start', c='#b02a1f' if i == 5 else '#333', bold=(i == 5))

o.extend(labels)
o.extend(top)
o.append('</svg>')
io.open(os.path.join(DOCS, 'perfboard_7x9.svg'), 'w', encoding='utf-8').write('\n'.join(o))

# ------------------------------------------------------------------ 목록 (markdown)
md = ['# 만능기판 꽂는 위치 목록 (7×9cm, 출력부 2채널) — 구상안', '',
      '그림: [perfboard_7x9.png](perfboard_7x9.png). 부품면에서 내려다보고 왼쪽 위 구멍이 (1, 1), 표기는 (열, 행). 30열 × 24행을 쓴다.', '',
      '기판에 올리는 것은 TENS 쪽뿐이다: 게이팅 PhotoMOS, 강도 사다리(R1 470Ω, R2 1kΩ, 바이패스 PhotoMOS 2개), 단자대. '
      '555 감시 회로, 트랜지스터, 게이팅용 330Ω, 우노 신호선은 브레드보드에 그대로 둔다.', '',
      '| 구역 | 행 | 내용 |', '|---|---|---|',
      '| CH1 TENS 쪽 | 1~7 | 단자대(2행), 사다리 저항(5행), 칩 3·4번 다리(7행) |',
      '| 절연 경계 | 8~9 | **전부 비움** |',
      '| 저전압 쪽 | 10~15 | 칩 1·2번 다리(10행, 15행), 330Ω, 핀헤더, GND 줄(12·13행) |',
      '| 절연 경계 | 16~17 | **전부 비움** |',
      '| CH2 TENS 쪽 | 18~24 | CH1의 위아래 거울상. 칩은 180° 돌려 꽂는다 |', '',
      '## 부품', '', '| 부품 | 구멍 |', '|---|---|']
md += [f'| {n} | {w} |' for n, w in md_parts]
md += ['', '## 뒷면 배선', '', '| 넷 | 무엇 | 지나는 구멍 |', '|---|---|---|']
md += [f'| {n} | {w} | {p} |' for n, w, p in md_wires]
md += ['', '## 바깥 연결', '',
       '| 기판 | 연결 대상 |', '|---|---|',
       '| CH1 IN 단자 (5,2) | TENS CH1 리드 A(빨강)의 기기 쪽 반 |',
       '| CH1 OUT 단자 (25,2) | 참가자 STOP NC1 한쪽. STOP 반대쪽에 리드 A의 패드 쪽 반 → 패드 A |',
       '| CH2 IN (5,23) / OUT (25,23) | TENS CH2 리드 A / 참가자 STOP NC2 |',
       '| H1 G1+ / G1− | 브레드보드 j20 / j21 (AQY 칩을 뺀 자리의 같은 세로줄) |',
       '| H1 G2+ / G2− | 브레드보드 j50 / j51 |',
       '| H2 LA1 / LB1 | 우노 D11 / D12 (330Ω은 기판에 있음) |',
       '| H2 LA2 / LB2 | 우노 A0 / A1 |',
       '| H2 GND | 우노 GND |', '',
       '리드 B(검정)는 자르지 않고 TENS에서 패드 B로 바로 간다. 브레드보드의 사다리 부품(17~27열, 47~57열)은 기판으로 옮기면 필요 없다.', '',
       '## 납땜 순서', '',
       '1. 부품을 꽂기만 하고 그림과 비교한다 (칩 방향, 저항 값).',
       '2. 저항 → 칩 → 핀헤더 → 단자대 순서로 납땜한다.',
       '3. 뒷면 배선은 저전압 쪽을 먼저, TENS 쪽을 나중에 한다. TENS 쪽은 피복선으로 짧게.',
       '4. 멀티미터로 TENS 쪽 ↔ 저전압 쪽, CH1 ↔ CH2가 무한대인지, 옆 구멍끼리 단락이 없는지 확인한다.',
       '5. LED 부하로 `ssr_blink.py`, `ladder_test.py`를 돌리고, 1kΩ 벤치 비교까지 통과한 뒤에 사람에게 연결한다.', '',
       '## 주의', '',
       '- 8·9행과 16·17행에는 납, 선, 부품을 두지 않는다. 줄 동박(스트립) 기판이면 이 줄의 동박을 끊는다.',
       '- 강도 사다리(v2.2)는 브레드보드에서 LED로 먼저 확인한 뒤 납땜한다.',
       '- CH1만 먼저 만들 때는 1~15행 가운데 CH1 부품과 H1의 G1+·G1−, H2의 LA1·LB1·GND만 납땜한다.', '']
io.open(os.path.join(DOCS, 'PERFBOARD.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
print('ok', len(used), 'holes')
