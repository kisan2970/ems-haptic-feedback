"""듀티 변조 확인용: 같은 길이의 반동을 듀티만 바꿔 차례로 낸다 (LED 부하 전용, 사람 연결 금지).
듀티는 세기가 아니라 '켜고 끄는 비율'이다. 50ms 주기 안에서 듀티 %만큼만 켜진다.
  듀티 100 = 계속 켜짐 / 50 = 25ms 켜고 25ms 끔 / 30 = 15ms 켜고 35ms 끔
  봉투 1(감쇠) = 100%에서 시작해 지정한 듀티까지 점점 줄어듦
사용: python duty_test.py COM17 1    (마지막 숫자: 채널 1 또는 2)
"""
import sys, time
import serial

port = sys.argv[1] if len(sys.argv) > 1 else 'COM11'
ch = int(sys.argv[2]) if len(sys.argv) > 2 else 1
DUR = 250                                   # 펌웨어 최대. 길어야 차이가 잘 보인다
STEPS = [(100, 0), (70, 0), (50, 0), (30, 0), (30, 1)]   # (듀티 %, 봉투)

def pkt(b):
    c = 0
    for x in b: c ^= ord(x)
    return f'${b}*{c:02X}\n'.encode()

ser = serial.Serial(port, 115200, timeout=0.05)
print('보드 리셋 대기...'); time.sleep(2.5)
ser.reset_input_buffer()
ser.write(pkt('A,1')); time.sleep(0.3)
if 'K,A,1' not in ser.read(4000).decode(errors='replace'):
    print('아밍 실패. D3가 GND에 연결됐는지 확인하세요.'); sys.exit(1)
print(f'아밍 완료. CH{ch}, 반동 {DUR}ms. Ctrl+C로 중단.\n')
try:
    for duty, env in STEPS:
        name = f'듀티 {duty}%' + (' 감쇠' if env else '')
        for k in range(3):
            ser.reset_input_buffer()
            ser.write(pkt(f'T,{ch},{DUR},{duty},{env}'))
            time.sleep(0.15)
            reply = [l for l in ser.read(4000).decode(errors='replace').split('\n') if l.startswith(('$K,T', '$E'))]
            print(f'{name:10s} {k+1}/3  {reply[0].strip() if reply else "응답 없음"}')
            t0 = time.time()
            while time.time() - t0 < 0.85:      # 반동 사이 1초 (예산: 10초에 3초 이내)
                ser.write(pkt('H')); time.sleep(0.2)
        print()
finally:
    ser.write(pkt('X')); ser.close(); print('정지')
