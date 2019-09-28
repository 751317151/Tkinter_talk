'''
@Author: 华豪
@Date: 2019-08-29 15:47:22
@E-Mail: hh@huahaohh.cn
@LastEditors: 华豪
@LastEditTime: 2019-09-23 09:13:12
'''

import tkinter as tk
import tkinter.messagebox
import socket
import threading
from multiprocessing import Process
from tkinter import filedialog
import os


def on_send_msg(chat_msg_box,chat_record_box):
    nick_name = "君哥"
    chat_msg = chat_msg_box.get(1.0, "end")
    if chat_msg == "\n":
        return

    chat_data = nick_name + ":" + chat_msg
    chat_data = chat_data.encode()
    data_len = "{:<15}".format(len(chat_data)).encode()
    
    try:
        sock.send(data_len)
        sock.send(chat_data)
    except:
        tk.messagebox.showerror("温馨提示", "发送消息失败，请检查网络连接！")
    else:
        chat_msg_box.delete(1.0, "end")
        chat_record_box.configure(state=tk.NORMAL)
        chat_record_box.insert("end", chat_data.decode() + "\n")
        chat_record_box.configure(state=tk.DISABLED)

def recv_chat_msg(chat_record_box):
    global sock
    while True:
        try:
            while True:
                msg_len_data = sock.recv(15)
                if not msg_len_data:
                    break

                msg_len = int(msg_len_data.decode().rstrip())
                recv_size = 0
                msg_content_data = b""
                while recv_size < msg_len:
                    tmp_data = sock.recv(msg_len - recv_size)
                    if not tmp_data:
                        break
                    msg_content_data += tmp_data
                    recv_size += len(tmp_data)
                else:
                    # 显示
                    chat_record_box.configure(state=tk.NORMAL)
                    chat_record_box.insert("end", msg_content_data.decode() + "\n")
                    chat_record_box.configure(state=tk.DISABLED)
                    continue
                break
        finally:
            sock.close()
            sock = socket.socket()
            sock.connect(("127.0.0.1", 9999))

def send_one_file(sock2, entry_filename):
    '''
    函数功能：将一个文件发送给客户端
    参数描述：
        sock_conn 套接字对象
        file_abs_path 待发送的文件的绝对路径
    '''
    file_abs_path = entry_filename.get()  #用get提取entry中的内容
    dest_file_parent_path = os.path.dirname(file_abs_path)

    file_name = file_abs_path[len(dest_file_parent_path):]

    if file_name[0] == '\\' or file_name[0] == '/':
        file_name = file_name[1:]

    file_size = os.path.getsize(file_abs_path)

    file_name = file_name.encode()
    file_name += b' ' * (300 - len(file_name))
    file_size = "{:<15}".format(file_size).encode()

    recv_list_op = b' '*14
    recv_type = b' '*8

    file_desc_info = recv_list_op + file_name + file_size + recv_type

    sock2.send(file_desc_info)
    with open(file_abs_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            sock2.send(data)
    tk.messagebox.showinfo("Bingo", "上传文件成功！")

def recv_one_file(sock2,entry_filename):
    recv_list_op = b' '*14

    file_name = entry_filename.get()  #用get提取entry中的内容
    file_name = file_name.encode()
    file_name += b' ' * (300 - len(file_name))

    file_size = b'1'*15

    file_type = b'download'

    file_desc_info = recv_list_op + file_name + file_size + file_type
    sock2.send(file_desc_info)

    while True:
        recv_list_op = sock2.recv(14).decode().rstrip()

        file_path = sock2.recv(300).decode().rstrip()
        print(file_path)
        if len(file_path) == 0:
            break

        file_size = sock2.recv(15).decode().rstrip() 
        if len(file_size) == 0:
            break
        file_size = int(file_size)

        file_type = sock2.recv(8).decode().rstrip()
        if len(file_type) == 0:
            break
        
        recv_size = 0

        f = open("E:\\FTP\\download\\"+file_path, "wb")

        while recv_size < file_size:
            if recv_size+100 >= file_size:
                file_data = sock2.recv(file_size-recv_size)
                f.write(file_data)
                break
            
            file_data = sock2.recv(100)
            f.write(file_data)
            
            recv_size += len(file_data)
        tk.messagebox.showinfo("Bingo", "下载文件成功！")

        f.close()
        break

def file_upload(sock2):
    file_up = tk.Tk()
    file_up.geometry('500x300+500+200')
    file_up.title("上传文件")

    def open_file():
        filename = filedialog.askopenfilename(title='选择文件', filetypes=[('All Files','*.*')])
        entry_filename.delete(0,"end")
        entry_filename.insert('insert', filename)
    # 设置button按钮接受功能
    button_import = tk.Button(file_up, text="选择文件", command=open_file)
    button_import.pack()
    # 设置entry
    entry_filename = tk.Entry(file_up, width=30, font=("宋体", 10, 'bold'))
    entry_filename.pack()

    tk.Button(file_up, text="上传", command=lambda:send_one_file(sock2,entry_filename)).pack()

    file_up.mainloop()

def file_download(sock2):
    file_down = tk.Tk()
    file_down.geometry('500x300+500+200')
    file_down.title("下载文件")
    # 收发服务端目录文件列表
    
    recv_list_op = b"recv_filenames"    # 给服务端发送请求，准备接收文件夹文件列表
    sock2.send(recv_list_op)
    
    file_length = sock2.recv(5).decode().rstrip()

    file_list = []
    for i in range(int(file_length)):
        file_list.append(sock2.recv(300).decode().rstrip())

    def printList(event):
        filename = mylist.get(mylist.curselection())
        entry_filename.delete(0,"end")
        entry_filename.insert('insert', filename)

    mylist=tkinter.Listbox(file_down,width=100) #列表框
    mylist.bind('<Double-Button-1>',printList)
    mylist.pack()

    for name in file_list:
        mylist.insert(tk.END,name)

    # 设置entry
    entry_filename = tk.Entry(file_down, width=30, font=("宋体", 10, 'bold'))
    entry_filename.pack()

    tk.Button(file_down, text="下载", command=lambda:recv_one_file(sock2,entry_filename)).pack()

    file_down.mainloop()

def talk(sock2):
    mainWnd = tk.Tk()
    mainWnd.title("P1901班专属聊天室")

    menubar = tk.Menu(mainWnd)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="上传", command=lambda:file_upload(sock2))
    filemenu.add_separator()


    filemenu.add_command(label="下载", command=lambda:file_download(sock2))
    filemenu.add_separator()
    menubar.add_cascade(label="文件", menu=filemenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Open")
    helpmenu.add_separator()
    menubar.add_cascade(label="帮助", menu=helpmenu)

    chat_record_box = tk.Text(mainWnd)
    chat_record_box.configure(state=tk.DISABLED)
    chat_record_box.pack(padx=10, pady=10)

    chat_msg_box = tk.Text(mainWnd)
    chat_msg_box.configure(width=65, height=5)
    chat_msg_box.pack(side=tk.LEFT,padx=10,pady=10)

    send_msg_btn = tk.Button(mainWnd, text="发 送", command=lambda:on_send_msg(chat_msg_box,chat_record_box))
    send_msg_btn.pack(side=tk.RIGHT, padx=10, pady=10, ipadx=15, ipady=15)

    threading.Thread(target=recv_chat_msg,args=(chat_record_box,)).start()

    mainWnd.config(menu=menubar)
    mainWnd.mainloop()
    sock.close()
    sock2.close()

if __name__ == '__main__':
    sock = socket.socket()
    sock.connect(("huahaohh.cn", 8888))

    sock2 = socket.socket()
    sock2.connect(("huahaohh.cn", 8887))
    
    threading.Thread(target=talk,args=(sock2,)).start()

    


