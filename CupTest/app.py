from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from flask import *
import paho.mqtt.client as paho
from paho import mqtt
import os
import json

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))
client = str()
app = Flask(__name__)  
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
line_bot_api = LineBotApi('uKu5Zv0ayrB1DguDCii/cjunGu2Wo75Yqg/40lnjEGWTETvccJ1nSKCCeP0JRzFnY6fueW8LQcJXjjiiq8hO6svyYKQvoHi+2JY4RVRgtOQNj7qnA6n9KRQktmRs1YzQ0rn4wgLJD+EXE4BefcWirQdB04t89/1O/w1cDnyilFU=')  
handler = WebhookHandler('8ae43dc297dedf445dcd182c0af2b798')

@app.route("/callback", methods=['POST'])
def callback():
    global client
    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

    # 啟用TLS(傳輸層安全協定)
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # 設定使用者名稱與密碼
    client.username_pw_set("Cup_post", "920828Asdd")
    # 與HiveMQ進行連結並設定Port為8883(加密的Port)
    client.connect("65c3954b06a741f381ece518ae641faf.s1.eu.hivemq.cloud", 8883)


    # 確定是LINE BOT的數位簽章標頭
    signature = request.headers['X-Line-Signature']
    # 求其內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # 處理webhook主體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#處理所接獲之數據並上傳
@handler.add(MessageEvent, message=TextMessage) 
def handle_message(event):     
        message = event.message.text
        messageList = str(message)
        messageList = messageList.lower()  
        messageList = list(messageList)
        if(len(messageList) == 6):
             for i in range(len(messageList)):
                if (messageList[i] > "f"):
                    messagetake = "輸入錯誤。請輸入正確的16進制(0~F)"
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(messagetake))
                    break
                if i == 5:
                    r = int(messageList[0],16) + int(messageList[1],16) * 16
                    g = int(messageList[2],16) + int(messageList[3],16) * 16
                    b = int(messageList[4],16) + int(messageList[5],16) * 16
                    messagetake = "r = {} , g = {} , b = {}".format(r,g,b)
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(messagetake))
                    MqttJson = {"r" : r , "g" : g , "b" : b}
                    MqttJson = json.dumps(MqttJson)
                    client.on_publish = on_publish
                    client.publish("TEST/CUPTEST", MqttJson, qos=0)
                    client.disconnect()
        elif(len(messageList) < 6):
            messagetake = "輸入少於位。請輸入16進制六位"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(messagetake))
        elif(len(messageList) > 6):
            messagetake = "輸入大於六位。請輸入16進制六位"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(messagetake))

if __name__ == "__main__":    
    port = int(os.environ.get('PORT', 5000))     
    app.run(host='0.0.0.0', port=port)