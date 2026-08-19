import pymysql

mysql=pymysql.connect(host="192.168.2.157",port=3306,user="root",passwd="123456",database="test")
cur=mysql.cursor()

def insert_operate(username,question,answer):
    sql=f"insert into users_history2(username,question,answer,is_valid) values('{username}','{question}','{answer}',1)"
    cur.execute(sql)
    mysql.commit()

def query_user_history(username):
    history=[]
    sql=f"select question,answer from users_history2 where username='{username}' and is_valid=1"
    cur.execute(sql)
    result=cur.fetchall()        # (("苹果","apple"),("梨子","pear"))  >  [{"role":"user","content":"苹果"},{"role":"assistant","content":"apple"}]
    for r in result:          # ("苹果","apple")
        question={"role":"user","content":r[0]}
        answer={"role":"assistant","content":r[1]}
        history.append(question)
        history.append(answer)
    return history

def insert_user(username,passwd):
    sql=f"insert into users values('{username}','{passwd}')"
    try:
        cur.execute(sql)
        mysql.commit()
    except Exception:
        return 1
    else:
        return 0

def update_history(username,history):
    sql=f"update users_history2 set is_valid=0 where username='{username}'"
    cur.execute(sql)
    sql=f"insert into users_history2(username,question,answer,is_valid) values('{username}','这是总结的内容','{history}',1)"
    cur.execute(sql)
    mysql.commit()