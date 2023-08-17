import os
import sys
import urllib.request
import json
from gtts import gTTS
from playsound import playsound

client_id = "1GkPFB7XDhB3BffQ8td0" # 개발자센터에서 발급받은 Client ID 값
client_secret = "pmoPS8ZFCx" # 개발자센터에서 발급받은 Client Secret 값

scrtext = input("번역할 텍스트를 입력하세요.: ")
encText = urllib.parse.quote(scrtext)
data = "source=ko&target=en&text=" + encText

url = "https://openapi.naver.com/v1/papago/n2mt"
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request, data=data.encode("utf-8"))
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    print(response_body.decode('utf-8'))
else:
    print("Error Code:" + rescode)

data2 = response_body.decode('utf-8')
data2 = json.loads(data2)
translated = data2['message']['result'].get('translatedText', None)

tts = gTTS(text=translated, lang='en', tld='com.au')
tts.save("ko2en3.mp3")
playsound('ko2en3.mp3')