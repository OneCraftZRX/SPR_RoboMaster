import socket  
import threading  
import time  
import random  
  
from loguru import logger  
  
  
def main():  
    s = socket.socket()  # 创建 socket 对象  
    # host = socket.gethostname()  # 获取本地主机名  
    host = "127.0.0.1"  
  
    logger.info('host name=' + str(host))  
    port = 7788  # 设置端口  
    s.bind((host, port))  # 绑定端口  
  
    s.listen(5)  # 等待客户端连接  
    logger.info("server start...")  
    c, addr = s.accept()  # 建立客户端连接  
    logger.info('连接地址：' + str(addr))  
    return c  
  
  
def send_message(c: socket):  
    while True:  
        time.sleep(random.randint(1, 5))  
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
        # 发送数据包
        c.send(('server test, time=' + timestamp).encode("utf-8"))  
        logger.debug("server send finish time=" + timestamp)  
  
  
def receive_message(c: socket):  
    while True:  
        recv_data = c.recv(1024)  
        if recv_data and len(recv_data) > 0:  
            logger.info(f"receive client message: " + recv_data.decode("utf-8"))  
  
  
if __name__ == "__main__":  
    c = None  
    try:  
        c = main()  
        t_send = threading.Thread(target=send_message, args=(c,))  
        t_receive = threading.Thread(target=receive_message, args=(c,))  
        t_send.start()  
        t_receive.start()  
    except KeyboardInterrupt:  
        if c and type(c) == socket:  
            c.close()  