'''
@Author: 华豪
@Date: 2019-09-22 17:59:17
@E-Mail: hh@huahaohh.cn
@LastEditors: 华豪
@LastEditTime: 2019-09-24 10:00:42
'''

import tkinter as tk
import tkinter.messagebox
import socket
import chat_client
import pymysql
from multiprocessing import Process
from PIL import ImageTk, Image


def check_user_login(userName,passwd):
    uname = userName.get()
    password = passwd.get()

    conn = pymysql.connect("127.0.0.1", 'hh', '92868520', 'chatdb')

    cur = conn.cursor()

    cur.execute("select * from users where uname = %s and passwd = md5(%s)",(uname,password))

    rows = cur.fetchall()

    cur.close()
    conn.close()
    
    if rows:
        chat_client.talk()
    else:
        tk.messagebox.showinfo("error","用户不存在或密码错误！")

def user_regist():

    regist = tk.Tk()
    regist.geometry('500x300+500+200')
    regist.title("噔噔等灯")

    rname = tk.Label(regist, text="用户名", bg="pink", font=("Arial",12), width=8, height=1)
    rname.place(x=100,y=20)
    userRegistName = tk.Entry(regist)
    userRegistName.configure(width=30)
    userRegistName.place(x=200,y=20)

    passwd = tk.Label(regist, text="密码", bg="pink", font=("Arial",12), width=8, height=1)
    passwd.place(x=100,y=60)
    rpasswd = tk.Entry(regist,show=("*"))
    rpasswd.configure(width=30)
    rpasswd.place(x=200,y=60)

    crpasswd = tk.Label(regist, text="确认密码", bg="pink", font=("Arial",12), width=8, height=1)
    crpasswd.place(x=100,y=100)
    cpasswd = tk.Entry(regist,show=("*"))
    cpasswd.configure(width=30)
    cpasswd.place(x=200,y=100)

    phone = tk.Label(regist, text="手机号", bg="pink", font=("Arial",12), width=8, height=1)
    phone.place(x=100,y=140)
    tphone = tk.Entry(regist)
    tphone.configure(width=30)
    tphone.place(x=200,y=140)

    email = tk.Label(regist, text="邮箱", bg="pink", font=("Arial",12), width=8, height=1)
    email.place(x=100,y=180)
    temail = tk.Entry(regist)
    temail.configure(width=30)
    temail.place(x=200,y=180)

    bregist = tk.Button(regist, text = "注 册", command=lambda:check_user_regist(userRegistName,rpasswd,cpasswd,tphone,temail,regist))
    bregist.place(x=220,y=220)

    regist.mainloop()

def check_user_regist(userRegistName,rpasswd,cpasswd,tphone,temail,regist):
    uname = userRegistName.get()
    password = rpasswd.get()
    cpassword = cpasswd.get()
    phone = tphone.get()
    email = temail.get()

    conn = pymysql.connect("127.0.0.1", 'hh', '92868520', 'chatdb')

    cur = conn.cursor()

    cur.execute("select * from users where uname = %s",(uname))

    rows = cur.fetchall()

    if rows:
        tk.messagebox.showinfo("error","用户名已存在！")
    elif password != cpassword:
        tk.messagebox.showinfo("error","两次密码不一致！")
    else:
        cur.execute("insert into users values(%s,md5(%s),%s,%s)",(uname,password,phone,email))
        conn.commit()

        tk.messagebox.showinfo("laalala","注册成功！")
        regist.destroy()

    cur.close()
    conn.close()

def user_login():
    login = tk.Tk()
    login.geometry('500x300+500+200')
    login.title("噔噔等灯")
    login.attributes("-alpha",0.95)

    # photo=tkinter.PhotoImage(file=r"fj.gif")
    # label=tkinter.Label(login,image=photo)  #图片
    # label.pack()


    lname = tk.Label(login, text="用户名", bg="pink", font=("Arial",12), width=8, height=1)
    lname.place(x=100,y=90)
    userName = tk.Entry(login)
    userName.configure(width=30)
    userName.place(x=200,y=90)

    lpasswd = tk.Label(login, text="密码", bg="pink", font=("Arial",12), width=8, height=1)
    lpasswd.place(x=100,y=130)
    passwd = tk.Entry(login,show=("*"))
    passwd.configure(width=30)
    passwd.place(x=200,y=130)

    blogin = tk.Button(login, text = "登 陆", command=lambda:check_user_login(userName,passwd))
    blogin.place(x=140,y=180)
    bregist = tk.Button(login, text = "注 册", command=thread_regist)
    bregist.place(x=220,y=180)

    login.mainloop()

def thread_regist():
    Process(target=user_regist).start()

if __name__ == '__main__':
    sock = socket.socket()
    sock.connect(("127.0.0.1", 9999))
    Process(target=user_login).start()



    sock.close()