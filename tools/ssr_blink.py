"""PhotoMOS 출력 확인용: 2초 켜고 2초 끄기를 반복한다 (TENS 미연결 상태 전용).
멀티미터를 부저 모드로 두고 CH1은 a20·a21, CH2는 a50·a51 구멍에 리드를 댄 채 실행.
켜진 2초 동안 삐 소리가 나고, 꺼진 2초 동안 조용하면 정상.
사용: python ssr_blink.py COM11 1    (마지막 숫자: 1=CH1, 2=CH2, 3=둘 다)
"""
import sys, time, threading
import serial

port = sys.argv[1] if len(sys.argv) > 1 else 'COM11'
mask = int(sys.argv[2]) if len(sys.argv) > 2 else 1
def pkt(b):
    c = 0
    for ch in b: c ^= ord(ch)
    return f'${b}*{c:02X}\n'.encode()
ser = serial.Serial(port, 115200, timeout=0.05)
print('보드 리셋 대기...'); time.sleep(2.5)
ser.reset_input_buffer()
ser.write(pkt('A,1')); time.sleep(0.3)
reply = ser.read(4000).decode(errors='replace')
if 'K,A,1' not in reply:
    print('아밍 실패. D3가 GND에 연결됐는지 확인하세요.'); sys.exit(1)
print(f'아밍 완료. 채널 마스크 {mask}. Ctrl+C로 중단.')
try:
    for cycle in range(8):
        print(f'[{cycle+1}/8] 켬 (2초)  ← 삐 소리가 나야 함'); t0 = time.time()
        while time.time() - t0 < 2.0:
            ser.write(pkt(f'W,{mask}')); time.sleep(0.1)
        ser.write(pkt('W,0'))
        print(f'[{cycle+1}/8] 끔 (2초)  ← 조용해야 함'); t0 = time.time()
        while time.time() - t0 < 2.0:
            ser.write(pkt('H')); time.sleep(0.2)
finally:
    ser.write(pkt('X')); ser.close(); print('정지')
