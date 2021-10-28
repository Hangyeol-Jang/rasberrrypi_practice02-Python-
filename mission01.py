# -*- coding: utf-8 -*-
# MISSION 01
# 음성으로 로그인
# 회원정보를 화면에 출력
# 채팅 프로그램에 입장
# 채팅 입력 및 종료

import socket
from _thread import *
import time

# 로그인 요청
import requests

# stt 모듈을 임포트
from mission01_stt import getVoice2Text

# tts 모듈 임포트
from mission01_tts import getText2VoiceStream
import MicrophoneStream as MS

# 채팅 프로그램 접속 주소
HOST = "115.85.182.118"
PORT = 43503

def chatting(user):
	print("접속 중 ...")
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect( (HOST, PORT) )
	print("접속 성공")
	
	# 수신 함수를 선언합니다. 해당 기능에서만 사용할 것이므로, 함수 안에서 함수를 선언했습니다.
	def execute():
		while True:
			print()
			data = client_socket.recv(1024)
			print("Received", repr(data.decode("ms949")) )

	print("쓰레드 실행")
	start_new_thread( execute, () )

	print("입력 시작")
	client_socket.sendall(  (user +"\n" ).encode("ms949") )
	while True:
		# stt로 채팅 내용을 받습니다.
		ctx = getVoice2Text()
		
		# 종료라고 입력하면 채팅 연결을 종료합니다.
		if  ctx=="종료":
			break
			
		client_socket.sendall(  (ctx +"\n" ).encode("ms949") )

	client_socket.close()
	
def login():
	print("로그인을 진행합니다")
	print()
	print("아이디를 말씀해주세요")
	user = getVoice2Text()
	
	print("패스워드를 말씀해주세요")
	pw = getVoice2Text()
	
	r = requests.post("http://192.168.0.30:8080/mission01login",data={"id":user, "pw":pw}).text
	
	if r=="":
		print("존재하지 않는 유저입니다.")
		return None
	else:
		output_file = "testtts.wav"
		getText2VoiceStream("{0} 님 환영합니다!!!           아!!!".format(r) , output_file)
		MS.play_file(output_file)
		return r

def main():
	
	user = login()
	
	if user is not None:
		chatting(user)
	
	print("프로그램 종료")

if __name__ == '__main__':
    main()
