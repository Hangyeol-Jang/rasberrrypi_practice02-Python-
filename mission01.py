# -*- coding: utf-8 -*-
# MISSION 01
# 음성으로 로그인
# 회원정보를 화면에 출력
# 채팅 프로그램에 입장
# 채팅 입력 및 종료

import socket
from _thread import *
import time

# stt 모듈을 임포트
from mission01_stt import getVoice2Text

# 채팅 프로그램 접속 주소
HOST = "115.85.182.118"
PORT = 43503

def chatting():
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
	while True:
		# stt로 채팅 내용을 받습니다.
		ctx = getVoice2Text()
		
		# 종료라고 입력하면 채팅 연결을 종료합니다.
		if  ctx=="종료":
			break
			
		client_socket.sendall(  (ctx +"\n" ).encode("ms949") )

	client_socket.close()

def main():
	
	
	chatting()
	
	print("프로그램 종료")

if __name__ == '__main__':
    main()
