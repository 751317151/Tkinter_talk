'''
@Author: 华豪
@Date: 2019-08-29 14:39:42
@E-Mail: hh@huahaohh.cn
@LastEditors: 华豪
@LastEditTime: 2019-08-29 17:16:37
'''

import socket
import threading


# UDP打洞
# 定长包头(158) + 变长聊天信息(昵称:聊天内容)

def client_chat(sock_conn, client_addr):
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

sock_listen = socket.socket()
sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_listen.bind(("0.0.0.0", 9999))
sock_listen.listen(5)

client_socks = []

while True:
    sock_conn, client_addr = sock_listen.accept()
    client_socks.append((sock_conn, client_addr))
    threading.Thread(target=client_chat, args=(sock_conn, client_addr)).start()


