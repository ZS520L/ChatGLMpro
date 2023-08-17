from flask import Flask, request, Response
import json
import requests
import zhipuai

# your api key
zhipuai.api_key = "f21ad16920147a28d6b8ab71b3e9c440.q4tDzJJRYEUDbPsP"


'''
  说明：
  add: 事件流开启
  error: 平台服务或者模型异常，响应的异常事件
  interrupted: 中断事件，例如：触发敏感词
  finish: 数据接收完毕，关闭事件流
'''

def sse_invoke_example(question):
    response = zhipuai.model_api.sse_invoke(
        model="chatglm_pro",
        prompt=question,
        top_p=0.7,
        temperature=0.9,
    )

    for event in response.events():
        if event.event == "add":
            try:		
                yield 'data: {"id":"chatcmpl-mJCgVYn7BNtc","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant","content":"'+event.data+'"}}],"finish_reason":null}\n\n'
            except:
                pass
        elif event.event == "error" or event.event == "interrupted":
            try:		
                yield 'data: {"id":"chatcmpl-mJCgVYn7BNtc","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant","content":"'+event.data+'"}}],"finish_reason":null}\n\n'
            except:
                pass
        elif event.event == "finish":
            try:		
                yield 'data: {"id":"chatcmpl-mJCgVYn7BNtc","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant","content":"'+event.data+'"}}],"finish_reason":null}\n\n'
            except:
                pass
            yield 'data: {"id":"chatcmpl-mJCgVYn7BNtc","object":"chat.completion.chunk","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"finish_reason":"stop"}\n\n'
            yield 'data: [DONE]\n\n'
        else:
            try:		
                yield 'data: {"id":"chatcmpl-mJCgVYn7BNtc","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant","content":"'+event.data+'"}}],"finish_reason":null}\n\n'
            except:
                pass


app = Flask(__name__)

@app.route('/', methods=['POST'])
def return_post_content():
	
    content = request.get_data() # 获取POST请求的内容
    data = json.loads(content) # 解析JSON字符串

    messages = data.get("messages") # 获取messages字段的值
    data = json.dumps(messages)

    return Response(sse_invoke_example(eval(data)), mimetype='text/event-stream')
	

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')