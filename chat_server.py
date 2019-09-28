'''
@Author: 华豪
@Date: 2019-08-29 14:39:42
@E-Mail: hh@huahaohh.cn
@LastEditors: 华豪
@LastEditTime: 2019-08-29 17:16:37
'''

import socket
import threading
import os


# UDP打洞
# 定长包头(158) + 变长聊天信息(昵称:聊天内容)

def client_chat(sock_conn, client_addr,client_socks):
    try:
        while True:
            msg_len_data = sock_conn.recv(15)
            if not msg_len_data:
                break

            msg_len = int(msg_len_data.decode().rstrip())
            recv_size = 0
            msg_content_data = b""
            while recv_size < msg_len:
                tmp_data = sock_conn.recv(msg_len - recv_size)
                if not tmp_data:
                    break
                msg_content_data += tmp_data
                recv_size += len(tmp_data)
            else:
                # 发送给其他所有在线的客户端
                for sock_tmp, tmp_addr in client_socks:
                    if sock_tmp is not sock_conn:
                        try:
                            sock_tmp.send(msg_len_data)
                            sock_tmp.send(msg_content_data)
                        except:
                            client_socks.remove((sock_tmp, tmp_addr))
                            sock_tmp.close()
                continue
            break

    finally:
        client_socks.remove((sock_conn, client_addr))
        sock_conn.close()

def receive_file(sock):
    while True:
        while True:
            while True:
                recv_list_op = sock.recv(14).decode().rstrip()
                if recv_list_op:
                    send_filelist(sock)
                else:
                    break
                
            file_path = sock.recv(300).decode().rstrip() 
            if len(file_path) == 0:
                break

            file_size = sock.recv(15).decode().rstrip() 
            if len(file_size) == 0:
                break
            file_size = int(file_size)

            file_type = sock.recv(8).decode().rstrip()
            if len(file_type):
                send_one_file(sock,file_path)
                break

            recv_size = 0

            f = open("./Tkinter_files/"+file_path, "wb")

            while recv_size < file_size:
                if recv_size+100 >= file_size:
                    file_data = sock.recv(file_size-recv_size)
                    f.write(file_data)
                    break
                
                file_data = sock.recv(100)
                f.write(file_data)
                
                recv_size += len(file_data)

            f.close()

def send_filelist(sock):
    filelist = os.listdir("./Tkinter_files/")
    file_length = len(filelist)
    
    file_length = "{:<5}".format(file_length).encode()
    sock.send(file_length)

    for filename in filelist:
        filename = filename.encode()
        filename += b' ' * (300 - len(filename))
        sock.send(filename)

def send_one_file(sock, file_path):
    '''
    函数功能：将一个文件发送给客户端
    参数描述：
        sock_conn 套接字对象
        file_abs_path 待发送的文件的绝对路径
    '''
    recv_list_op = b' '*14

    file_name = file_path
    file_size = os.path.getsize("./Tkinter_files/" + file_path)

    file_name = file_name.encode()
    file_name += b' ' * (300 - len(file_name))
    file_size = "{:<15}".format(file_size).encode()

    file_type = b'download'

    file_desc_info = recv_list_op + file_name + file_size + file_type
    sock.send(file_desc_info)

    with open("./Tkinter_files/" + file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            sock.send(data)

def recv_chat():
    sock_listen = socket.socket()
    sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_listen.bind(("0.0.0.0", 8888))
    sock_listen.listen(5)

    client_socks = []

    while True:
        sock_conn, client_addr = sock_listen.accept()
        client_socks.append((sock_conn, client_addr))
        threading.Thread(target=client_chat, args=(sock_conn, client_addr,client_socks)).start()

def recv_send_file():
    sock_listen_file = socket.socket()
    sock_listen_file.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_listen_file.bind(("0.0.0.0", 8887))
    sock_listen_file.listen(5)

    client_socks = []

    while True:
        sock, client_addr = sock_listen_file.accept()
        client_socks.append((sock, client_addr))
        threading.Thread(target=receive_file, args=(sock,)).start()


if __name__ == '__main__':
    threading.Thread(target=recv_chat).start()
    threading.Thread(target=recv_send_file).start()

