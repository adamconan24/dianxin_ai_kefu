import asyncio
import requests,os,json
from prompts import prompt
from get_mysql import *

api_key=os.getenv("DEEPSEEK_API_KEY")
base_url="https://api.deepseek.com"
h={"Content-Type":"application/json","Authorization":f"Bearer {api_key}"}

messages={"role":"system","content":prompt}

def summary(username,history):
    datas={
        "model":"deepseek-v4-flash",
        "temperature":0.2,
        "max-tokens":256,
        "stream":False,
        "messages":history
    }
    current_prompt={"role":"system","content":'总结我输入的内容，提炼里面的重点部分的数据，要保留对用户的身份和名字的记忆，以及用户的提问的主要内容。对字符内容进行结构上的压缩，只需要保留重点即可。整个回复不需要除了总结内容之外的其他任何表情、特殊符号、提示信息等，长度不超过200个字'}
    history.insert(0,current_prompt)
    response=requests.post(base_url+"/chat/completions",headers=h,json=datas,timeout=30)
    r=response.json()['choices'][0]['message']['content'] 
    # 将当前的结果写入数据库当成最新的数据来存储，之前所有的内容都是0的失效数据
    update_history(username,r)
    result=[{"role":"assistant","content":r}]
    return result


def get_answer(username,question):
    history=query_user_history(username)      # 按照用户名查询这个用户所有的历史记录
    # 现在将数据的提炼，写成自动的判断，每次都读取当前history有多少行数据，如果到达5行限制，就将它们当成一个整体进行数据的提炼
    print(len(history))
    if len(history)>=6:           # 因为一次提问是一个字典，一个回答是一个字典，一次交互占两个长度
        history=summary(username,history)

    history.insert(0,messages)                # 在历史记录的第一个位置，添加系统的提示词信息
    history.append({"role":"user","content":question})

    datas={
        "model":"deepseek-v4-flash",
        "temperature":0.2,
        "max-tokens":512,
        "stream":False,
        "messages":history
    }

    response=requests.post(base_url+"/chat/completions",headers=h,json=datas,timeout=30)
    r=response.json()['choices'][0]['message']['content']    # 在收到大模型的回答之后，将回答的内容也拼接进来
    insert_operate(username,question,r)
    return r


async def get_stream_answer(question):
        print("deepseek接到的问题：",question)
        datas={
            "model":"deepseek-v4-flash",
            "temperature":0.2,
            "max-tokens":512,
            "stream":True,                  # 打开流式显示的开关
            "messages":[{"role":"system","content":prompt},{"role":"user","content":question}]
        }

        # 在post的接口请求中，也要添加一个stream的流式的参数
        response=requests.post(base_url+"/chat/completions",headers=h,json=datas,timeout=30,stream=True)
        for line in response.iter_lines():      # 流式处理是以行的方式进行数据的循环和迭代
            # 将每一行的数据，先处理成utf-8的格式
            line=line.decode("utf-8")           # decode是解码字符串
            # 当前line是用 "data: "开头的，要将这个数据删除掉
            line=line[6:]
            try:
                if line=='[DONE]':      # 如果遇到了[DONE]关键字，说明数据已经全部运行完成了，后面没有其他的内容了
                    break 
                else:
                    line=json.loads(line)      # 将获取到的每一行的json格式，转换成了字典的格式
                    r=line['choices'][0]['delta']['content']      # 对返回需要的内容进行提取
                    # 有的行数据的返回，里面其实并没有内容，是一个空的数据，如果当前行没有返回数据，直接跳过，进行下一次的循环
                    if r=="" or r is None or r=="None":
                        continue
                    yield r                     # 在流式回答中，通过yield关键字提取每一次出现的数据
                    await asyncio.sleep(0.01)
            except Exception:
                pass

















