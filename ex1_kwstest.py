#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example 1: GiGA Genie Keyword Spotting"""

from __future__ import print_function

import audioop
from ctypes import *
import RPi.GPIO as GPIO
import ktkws # KWS
import MicrophoneStream as MS
KWSID = ['기가지니', '지니야', '친구야', '자기야']
RATE = 16000
CHUNK = 512

## 소스코드에서 사용된 라이브러리에 대해서 알아보도록 하겠습니다.
## audioop : 오디오를 조작하는 모듈로, 원신호(음성 데이터)를 가공하는데 사용됩니다.
## ctypes : python용 외부 함수(foregin function) 라이브러리 모듈로, 
##					ALSA configure에서 발생하는 Error Handler를 조작할 때 사용됩니다.
## RPi.GPIO : 라즈베리파이의 GPIO를 사용하여 아케이드 스위치의 입력과 LED를 제어하는 라이브러리입니다.
## ktkws : 키워드 검출 모듈로 호출어 검출 및 사용에 관한 함수들이 정의되어 있습니다.
## MicrophoneStream : 마이크를 조작하는 모듈로, 마이크를 통해 음성 신호를 입력받을 대 사용됩니다.

# GPIO 설정을 진행해주는 부분입니다. 버튼의 LED의 초기 설정과 버튼이 눌러졌을 때의 동작을 처리해줍니다.
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(31, GPIO.OUT)
btn_status = False

def callback(channel):  
	print("falling edge detected from pin {}".format(channel))
	global btn_status
	btn_status = True
	print(btn_status)

GPIO.add_event_detect(29, GPIO.FALLING, callback=callback, bouncetime=10)
## GPIO를 사용하여 AMK의 버튼의 입력 상태를 확인하는 소스코드입니다.
## 아케이드 버튼의 스위치와 연결되어 있는 핀인 29번을 풀업 입력으로 설정하고,
## 아케이드 스위치의 LED가 연결되어 있는 31번 핀을 출력 핀으로 설정합니다.
## callback 함수를 사용하여 버튼이 눌려졌을 때를 이벤트 발생으로 처리하여 나중에 호출어 인식 대신 사용할 수 있도록 처리해줍니다.

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)
## ALSA(Advanced Linux Sound Architecture)의 설정으로 인해 발생하는 불필요한 에러 메시지를
## 삭제하기 위한 Python Error Handler를 정의하는 부분입니다.

# 마이크에서 들어오는 데이터를 호출어 인식하는 모듈을 사용하여 동작하는 함수입니다.
# 마이크 데이터에서 호출어가 인식되면 '띠리링' 소리를 출력합니다.
def detect():
	with MS.MicrophoneStream(RATE, CHUNK) as stream:
		audio_generator = stream.generator()
## 마이크 사용을 도와주는 MicrophoneStream 클래스를 이용해 음성데이터를 어떻게(RATE, CHUNK) 가져올지를 설정하고,
## audio_generator 변수에 마이크로 입력된 음성데이터를 generator()를 이용하여 전달합니다.

## audio_generator로부터 음성 데이터를 받아와 content에 할당합니다.
		for content in audio_generator:

## 입력된 음성(content) 데이터에 호출어가 포함되어 있는지를 확인합니다. 만약 호출어가 포함되어 있다면, rc 변수에 1이 저장되고,
## 포함되지 않았다면 rc에 0이 저장됩니다.
			rc = ktkws.detect(content)
## 마이크를 통해 입력되고 있는 음성데이터(content)의 음량을 숫자로 출력해주는 매서드입니다.
## print 함수가 주석으로 처리되어 출력의 결과 값이 출력되지는 않습니다.
			rms = audioop.rms(content,2)
			#print('audio rms = %d' % (rms))

## ktws를 통해 호출어가 인식되면 rc 변수에 1이 저장되기 때문에 1이 인식될 때 "띠리링" 소리를 출력해주고, 함수에서 200을 리턴하도록 합니다.
			if (rc == 1):
				MS.play_file("../data/sample_sound.wav")
				return 200

# 버튼이 눌리는 것을 처리해주는 부분입니다. 버튼이 눌러진 것을 확인하면 "띠리링" 소리를 출력해줍니다.
def btn_detect():
	global btn_status
	with MS.MicrophoneStream(RATE, CHUNK) as stream:
		audio_generator = stream.generator()

		for content in audio_generator:
			GPIO.output(31, GPIO.HIGH)
			rc = ktkws.detect(content)
			rms = audioop.rms(content,2)
			#print('audio rms = %d' % (rms))
			GPIO.output(31, GPIO.LOW)
			if (btn_status == True):
				rc = 1
				btn_status = False			
			if (rc == 1):
				GPIO.output(31, GPIO.HIGH)
				MS.play_file("../data/sample_sound.wav")
				return 200
## 소스코드 설명 4와 거의 동일하며 버튼이 눌러졌을 때의 btn_status가 True 일 때와 호출어가
## 인식되었을 때 각각 rc 변수에 1을 저장하여 "띠링 소리와 200을 리턴하는 함수입니다.

# 마이크로 호출어를 인식하는 함수를 실행하고 진행 상황을 출력해주는 함수입니다. 여기서 기가지니, 지니야, 자기야, 친구야의
# 호출어를 지정할 수 있습니다.
def test(key_word = '기가지니'):
	rc = ktkws.init("../data/kwsmodel.pack")
## 미리 호출어들이 학습된 음성데이터를 이용하여 ktkws 모듈을 초기화합니다.
## 최기화에 문제가 없다면 1을 출력합니다.
	print ('init rc = %d' % (rc))
	rc = ktkws.start()
	print ('start rc = %d' % (rc))
	print ('\n호출어를 불러보세요~\n')
## ktkws모듈의 동작을 시작합니다.
## 모듈이 문제없이 시작되면 10을 출력하고, "호출어를 불러보세요~~" 를 출력합니다.
	ktkws.set_keyword(KWSID.index(key_word))
	rc = detect()
	print ('detect rc = %d' % (rc))
	print ('\n\n호출어가 정상적으로 인식되었습니다.\n\n')
	ktkws.stop()
	return rc

## 함수의 인자 값으로 사용된 key_word 변수의 값을 이용하여 4개의 호출어 중 어떤 호출어를 이용하여 인식할지 설정합니다.
## 그다음 소스코드 설명4의 detect() 함수를 실행하여 마이크 입력을 통해 호출어가 인식되는 것을 확인합니다.
## 호출어가 인식되었다면 detect 함수에서 200을 리턴받고, 결과를 출력합니다. 마지막으로 ktkws 모듈을 멈추고,
## detect 함수에서 입력받은 200을 리턴해줍니다.

# 버튼을 인식하는 함수를 실행하고 진행 상황을 출력해주는 함수입니다.
def btn_test(key_word = '기가지니'):
	global btn_status
	rc = ktkws.init("../data/kwsmodel.pack")
	print ('init rc = %d' % (rc))
	rc = ktkws.start()
	print ('start rc = %d' % (rc))
	print ('\n버튼을 눌러보세요~\n')
	ktkws.set_keyword(KWSID.index(key_word))
	rc = btn_detect()
	print ('detect rc = %d' % (rc))
	print ('\n\n호출어가 정상적으로 인식되었습니다.\n\n')
	ktkws.stop()
	return rc

## 이 부분도 소스코드 6과 비슷하게 동작하며, 버튼의 상태 값을 가지고 오기 위해서 global btn_status로 전역변수를 가져옵니다.
## 또한 detect() 함수가 아닌 btn_detect() 함수를 사용하여 버튼이 눌러졌을 때도 호출어가 인식된 것과 같이 동작하게 됩니다.

def main():
	test()

if __name__ == '__main__':
	main()
