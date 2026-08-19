import os,requests
import dashscope

api_key=os.getenv("DASHSCOPE_API_KEY")
dashscope.base_http_api_url="https://dashscope.aliyuncs.com/api/v1"   # Qwen的多模态操作的地址

def get_image_info(img_url,text):
    messages=[
        {"role":"user",
        "content":[
            {"image":img_url},
            {"text":text}
        ]}
    ]

    response=dashscope.MultiModalConversation.call(
        api_key=api_key,
        model="qwen3.7-plus",
        messages=messages,
        max_tokens=256
    )

    return response['output']['choices'][0]['message']['content'][0]['text']


def set_image(text,local_path):
    messages=[
        {"role":"user",
        "content":[
            {"text":text}
        ]}
    ]   
    response=dashscope.MultiModalConversation.call(
        api_key=api_key,
        model="qwen-image-2.0-pro",           # 调用生图的模型
        messages=messages,
        result_format='message',
        stream=False
    )
    url=response['output']['choices'][0]['message']['content'][0]['image']    # 获取qwen生成的图片的老地址
    r=requests.get(url)       # 使用地址获取图片的二进制数据
    with open(local_path,"wb")  as f:     # 使用open的方式将二进制的数据写入到一个文件中进行保存
        f.write(r.content)

set_image('生成一个分辨率是256*256的图片，内容是一只金毛狗在海边奔跑',"E:/test/jinmao01.png")

def set_music():
    base_url="https://dashscope.aliyuncs.com/api/v1/services/audio/music/generation"
    h={
        "Content-Type":"application/json",
        "Authorization":f"Bearer {api_key}"
    }
    data={
        "model": "fun-music-preview",
        "input": {
            "prompt": "夏日清新民谣，木吉他与口琴伴奏，轻快节奏，适合旅行Vlog背景音乐",
            "gender": "female"
        }
    }
    res=requests.post(url=base_url,headers=h,json=data)
    print(res)

set_music()
