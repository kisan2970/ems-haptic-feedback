"""강도 사다리 확인용: 단계 3 → 2 → 1 → 0으로 내리며 2초씩 켠다 (LED 부하 전용, 사람 연결 금지).
펌웨어 v2.2 이상. 단계가 내려갈수록 LED가 어두워지면 정상.
  3 = 둘 다 바이패스(노브 세기 그대로) / 2 = R1 470Ω 들어감 / 1 = R2 1kΩ 들어감 / 0 = 둘 다 들어감
사용: python ladder_test.py COM17 1    (마지막 숫자: 채널 1 또는 2)
"""
import sys, time
import serial

port = sys.argv[1] if len(sys.argv) > 1 else 'COM11'
ch = int(sys.argv[2]) if len(sys.argv) > 2 else 1

def pkt(b):
    c = 0
    for x in b: c ^= ord(x)
    return f'${b}*{c:02X}\n'.encode()

def ask(ser, body, want):
    ser.reset_input_buffer(); ser.write(pkt(body)); time.sleep(0.15)
    lines = [l.strip() for l in ser.read(4000).decode(errors='replace').split('\n') if l.startswith(('$K', '$E', '$I'))]
    return any(want in l for l in lines), lines

ser = serial.Serial(port, 115200, timeout=0.05)
print('보드 리셋 대기...'); time.sleep(2.5)
boot = ser.read(4000).decode(errors='replace')
if 'LADDER' not in boot:
    print('경고: 부팅 메시지에 LADDER가 없다. 펌웨어 v2.2를 올렸는지 확인하세요.')
ok, _ = ask(ser, 'A,1', 'K,A,1')
if not ok:
    print('아밍 실패. D3가 GND에 연결됐는지 확인하세요.'); sys.exit(1)
print(f'아밍 완료. CH{ch}. Ctrl+C로 중단.\n')
try:
    for rnd in range(2):
        for lv in (3, 2, 1, 0):
            ok, lines = ask(ser, f'L,{ch},{lv}', f'K,L,{ch},{lv}')
            print(f'[{rnd+1}/2] 강도 {lv}  켬 2초  {"" if ok else "응답 이상: " + " / ".join(lines)}')
            t0 = time.time()
            while time.time() - t0 < 2.0:
                ser.write(pkt(f'W,{ch}')); time.sleep(0.1)
            ser.write(pkt('W,0'))
            t0 = time.time()
            while time.time() - t0 < 1.0:
                ser.write(pkt('H')); time.sleep(0.2)
finally:
    ser.write(pkt(f'L,{ch},3')); ser.write(pkt('X')); ser.close(); print('정지 (강도 3으로 되돌림)')
