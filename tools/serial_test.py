"""우노/ESP32 펌웨어 시리얼 응답 자동 점검. 사용: python serial_test.py COM11"""
import sys, time
import serial

port = sys.argv[1] if len(sys.argv) > 1 else 'COM11'

def cs(body):
    c = 0
    for ch in body: c ^= ord(ch)
    return f'${body}*{c:02X}\n'

def read_for(ser, sec, show_sensor=1):
    end = time.time() + sec; lines = []; shown = 0
    while time.time() < end:
        l = ser.readline().decode(errors='replace').strip()
        if not l: continue
        if l.startswith('$S,'):
            if shown < show_sensor: print('   ', l); shown += 1
            continue
        print('   ', l); lines.append(l)
    return lines

with serial.Serial(port, 115200, timeout=0.1) as ser:
    print(f'[{port}] 열림, 부팅 대기 (보드 자동 리셋)')
    read_for(ser, 2.5, show_sensor=2)
    steps = [('H', '하트비트'), ('A,1', '아밍 (D3가 GND 아니면 E,2가 정상)'),
             ('T,1,100,100,0', '자극 100ms (아밍 안 됐으면 E,4가 정상)'), ('X', '정지'),
             ('Z', '알 수 없는 명령 -> E,9')]
    for body, desc in steps:
        print(f'> {cs(body).strip()}   ({desc})')
        ser.write(cs(body).encode()); read_for(ser, 0.4, show_sensor=0)
    print('> 체크섬 틀린 명령 $H*00 -> E,6 기대')
    ser.write(b'$H*00\n'); read_for(ser, 0.4, show_sensor=0)
    print('> 무게 유지 $W,1 을 0.1초 간격 1초 (아밍 안 됐으면 E,4 한 번)')
    for _ in range(10):
        ser.write(cs('W,1').encode()); time.sleep(0.1)
    read_for(ser, 0.1, show_sensor=0)
    print('> 전송 중단 후 0.4초 대기 (아밍됐으면 K,W,1,0 기대)')
    read_for(ser, 0.4, show_sensor=0)
