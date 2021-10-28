# -*- coding: utf-8 -*-

# 네이버 음성합성 Open API 예제
import os
import sys
import urllib.request

client_id = "1y7oxdyu70"
client_secret = "6WjCAcMYXVOe9Ic8PXOKjd0n5Iq1iaUpBmLijI9Y"
encText = urllib.parse.quote("반갑습니다 네이버")
data = "speaker=mijin&speed=0&text=" + encText;
url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
request = urllib.request.Request(url)
request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
request.add_header("X-NCP-APIGW-API-KEY",client_secret)
response = urllib.request.urlopen(request, data=data.encode('utf-8'))
rescode = response.getcode()

file_name = '1111.mp3'
if(rescode==200):
	print("TTS mp3 저장")
	response_body = response.read()
	with open(file_name, 'wb') as f:
		f.write(response_body)
else:
    print("Error Code:" + rescode)

