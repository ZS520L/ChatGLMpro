import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket
from flask import Flask, request, jsonify

# 创建 Flask 应用
app = Flask(__name__)



class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, ws1, ws2):
    pass
    # print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, question=ws.question, temperature=ws.temperature))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    global history
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content, end='')
        history = history + content
        if status == 2:
            history += '\n'
            ws.close()


def gen_params(appid, question, temperature):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {
            "chat": {
                "domain": "general",
                "random_threshold": temperature,
                "max_tokens": 4096,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data


def main(question, temperature, appid="15935bf1", api_secret="MGQ1YzE0MjljZTRkZDMxZjY5YzkzYWYx",
         api_key="32af57b18b91fd799d8917314666ac2b", gpt_url="ws://spark-api.xf-yun.com/v1.1/chat"):
    wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.temperature = temperature
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
@app.route('/')
def welcome():
    return "欢迎来到我的 Flask 网页！"
history = ''
@app.route('/ask', methods=['POST'])
def ask():
    global history
    history = ''
    question = request.json['question']
    temperature = request.json['temperature']
    main(question, temperature)
    return jsonify(answer=history.strip("\n"))
	
if __name__ == '__main__':
    app.run()
# if __name__ == "__main__":
    # # 测试时候在此处正确填写相关信息即可运行
    # while True:
        # prompt = input('\n请输入您的问题：')
        # history = history + 'User:' + prompt + '\n'
        # main(history)
        # # print('==\n', history)
