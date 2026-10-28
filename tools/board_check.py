"""브레드보드 조립 후 펌웨어·배선 자동 점검 (TENS 미연결 상태에서 실행).
사용: python board_check.py COM11
결과는 화면과 board_check_result.txt 에 저장.
"""
import sys, time, io, os, threading
import serial

port = sys.argv[1] if len(sys.argv) > 1 else 'COM11'
out = []
def log(s=''):
    out.append(s)
    try: print(s)
    except UnicodeEncodeError: pass

def pkt(body):
    c = 0
    for ch in body: c ^= ord(ch)
    return f'${body}*{c:02X}\n'.encode()

def verify(line):
    a, b = line.find('$'), line.rfind('*')
    if a < 0 or b < a or b + 3 > len(line): return None
    body = line[a + 1:b]; c = 0
    for ch in body: c ^= ord(ch)
    return body if f'{c:02X}' == line[b + 1:b + 3].upper() else None

results = []
def check(name, ok, detail=''):
    results.append((name, ok)); log(f"[{'OK ' if ok else 'NG '}] {name}  {detail}")

ser = serial.Serial(port, 115200, timeout=0.05)
lock = threading.Lock()
msgs, sens = [], []
stop = False
def reader():
    buf = b''
    while not stop:
        buf += ser.read(256)
        while b'\n' in buf:
            raw, buf = buf.split(b'\n', 1)
            body = verify(raw.decode(errors='replace').strip())
            if body is None: continue
            with lock:
                (sens if body.startswith('S,') else msgs).append((time.time(), body))
wlock = threading.Lock()
def send(b):
    with wlock: ser.write(pkt(b))
hb_on = False
def heartbeat():
    while not stop:
        if hb_on: send('H')
        time.sleep(0.2)
threading.Thread(target=reader, daemon=True).start()
threading.Thread(target=heartbeat, daemon=True).start()

def since(t0, kind='m'):
    with lock:
        src = msgs if kind == 'm' else sens
        return [b for t, b in src if t >= t0]

log(f'포트 {port}. 보드 리셋 대기 3초...')
time.sleep(3.0)
boot = [b for b in since(0) if b.startswith('I,')]
check('부팅 메시지 v2', any('v2' in m for m in boot), boot[0] if boot else '없음')
t0 = time.time(); time.sleep(1.0)
n = len(since(t0, 's'))
check('센서 스트림 약 100Hz', 90 <= n <= 110, f'{n}줄 / 1초')
last = since(0, 's')[-1].split(',')
ax, ay, az = int(last[7]), int(last[8]), int(last[9])
g = (ax * ax + ay * ay + az * az) ** 0.5 / 100
check('IMU 응답 (가속도 크기 약 1g)', 0.7 <= g <= 1.3, f'|a| = {g:.2f} g')
check('비상정지 입력 정상', last[-1] != '9', f'state {last[-1]}')

hb_on = True
t0 = time.time(); send('A,1'); time.sleep(0.4)
m = since(t0)
check('아밍 (D3 → GND 연결)', any(x.startswith('K,A,1') for x in m), ' / '.join(m) or '응답 없음')

for ch in (1, 2):
    t0 = time.time(); send(f'T,{ch},200,100,0'); time.sleep(0.5)
    m = since(t0); s = since(t0, 's')
    on = sum(1 for x in s if x.split(',')[-1] == '2')
    check(f'CH{ch} 반동 200ms', any(x.startswith(f'K,T,{ch}') for x in m), ' / '.join(m))
    check(f'CH{ch} 자극 중 상태가 약 0.2초', 15 <= on <= 25, f'{on}줄 = 약 {on*10}ms')

for ch in (1, 2):
    t0 = time.time()
    for _ in range(15):
        send(f'W,{ch}'); time.sleep(0.1)
    time.sleep(0.5)
    m = since(t0); s = since(t0, 's')
    on = sum(1 for x in s if x.split(',')[-1] == '2')
    ok = any(x.startswith(f'K,W,{ch},1') for x in m) and any(x.startswith(f'K,W,{ch},0') for x in m)
    check(f'CH{ch} 무게 1.5초 유지 후 해제', ok and 130 <= on <= 190, f'{" / ".join(m)}  자극 {on*10}ms')

t0 = time.time(); send('X'); time.sleep(0.3)
check('전부 정지', any(x.startswith('K,X') for x in since(t0)))
hb_on = False; stop = True; time.sleep(0.2); ser.close()

log('')
log(f'통과 {sum(ok for _, ok in results)} / {len(results)}')
io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'board_check_result.txt'), 'w', encoding='utf-8').write('\n'.join(out))
