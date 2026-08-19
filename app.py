# from flask import Flask, make_response, redirect, render_template,request,url_for
# from deepseek_chat import *
# from get_mysql import *

# app=Flask(__name__)

# @app.route("/",methods=["POST","GET"])
# def main():
#     username=request.cookies.get("username")

#     text=[]            # 使用一个列表，来存储所有的问答的数据
#     if username:       # 只要登录成功，那么就查询这个用户所有的历史数据
#         history=query_user_history(username)     # [{"role":"user","content":"苹果"},{"role":"assistant","content":"apple"}]
#         h=[i['content'] for i in history]     # [苹果,apple,梨子,pear]
#         for j in range(0,len(h),2):    # 0 2 4 6
#             text.append([h[j],h[j+1]])                # [[苹果,apple],[梨子,pear]]
#         if request.method=="GET":
#             text.reverse()                  # 在数据库中是按照时间做升序的排序，我们希望在页面中新的数据在上面，所以对数据做了一个反向输出的操作
#             return render_template("index.html",username=username,all_text=text)
#         elif request.method=="POST":
#             question=request.form.get("question")
#             # 向deepseek发送数据
#             answer=get_answer(username,question)
#             text.reverse()
#             return render_template("index.html",answer=answer,username=username,all_text=text)
#     else:
#         return render_template("register.html")

# @app.route("/register",methods=["POST","GET"])
# def register():
#     if request.method=="GET":
#         return render_template("register.html")
#     else:
#         username=request.form.get("username")
#         passwd=request.form.get("password")
#         r=insert_user(username,passwd)
#         if r==0:
#             res=make_response(redirect(url_for("main")))
#             res.set_cookie("username",username)
#             return res
#         else:
#             return render_template("register.html",result='注册失败，请重试')

# @app.route("/fanyi",methods=["GET","POST"])
# def fanyi():
#     if request.method == "GET":
#         words=request.args.get("words")
#     elif request.method == "POST":
#         datas=request.json
#         words=datas["words"]
#     r=get_answer(words)
#     return r

# @app.route("/logout")
# def logout():
#     res=make_response(redirect(url_for("register")))
#     res.delete_cookie("username")
#     return res

# if __name__=="__main__":
#     app.run(debug=True)


"""
现在不使用flask的框架了，flask不太能够进行流式数据的展示和处理，如果要使用flask，那么还要使用ajax等各种技术才能实现，先对比较复杂；
使用quart框架，使用方式和flask是一样的
"""
from quart import Quart, render_template, request, Response
from deepseek_chat import get_stream_answer

app=Quart(__name__)

# 创建主页的路由
@app.route("/")
async def main():
    return await render_template("index.html")

# 定义iframe子页面中的默认展示，刚开始进入页面是没有内容的
@app.route("/empty")
async def empty():
    return ''

# 定义ask接收数据的路由，以及通过接收的数据，来展示大模型的回答，对回答的内容进行子页面内容的拼接
@app.route("/ask",methods=["POST"])
async def ask():
    form = await request.form         # 因为是在异步的函数中读取数据，所以页面的数据要通过await来进行读取
    question=form.get("question")
    # 现在要将question传递给deepseek函数进行问答的获取，但是deepseek的函数是async异步的，读取异步函数的内容，要使用 async for 的
    # 方式来读取异步生成器的内容
    # 异步生成器也不能直接for循环，必须要放在一个异步的函数中才能执行
    async def generate_html():
        st="""<html>
        <head></head>
        <body>
            <div>
            <p>
        """
        yield st
        async for i in get_stream_answer(question):    # 只有deepseek返回文字是无法成为一个html的页面的，所以在前后要加上html
            yield i
        yield "</p></div></body></html>"
    # 在后台的框中，函数最后都是要返回一个html的页面的
    # 在当前的位置，通过 Response() 方式，构建一个html的页面，让函数进行返回
    return Response(
        generate_html(),            # 调用上面的函数，依次获取子页面中的html代码，拼接成一个完成的页面
        mimetype="text/html",       # mimetype是一个固定的关键字，在这个告诉函数我拼接的是一个文本构成的html
        headers={"Transform-Encoding":"chunked"}   # 这个将页面的数据定位为接收流式的切片数据
    )

# 启动服务器
if __name__=="__main__":
    app.run(debug=True)
