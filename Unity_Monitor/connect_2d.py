import socket  
import threading  
import time  
import random  
from loguru import logger  

# testarr="+1.00N-0.89N+0.78N-0.67N+0.56N-0.44N+0.33N+0.22N-0.11N+0.00N+1.00N-0.89N+0.78N-0.67N+0.56"

# def regenerate():
#     random_matrix = [[round(random.uniform(-1, 1), 2) for _ in range(3)] for _ in range(5)]
#     for row in random_matrix:
#         for i in range(len(row)):
#             while row[i] == 0:
#                 row[i] = round(random.uniform(-1, 1), 2)
#     # 将二维列表转换为字符串
#     result_string = ""
#     for row in random_matrix:
#         for num in row:
#             if num > 0:
#                 result_string += "+{:.2f}N".format(num)
#             else:
#                 result_string += "{:.2f}N".format(num)
#     result_string = result_string.rstrip("N")  # 移除末尾的N
#     return result_string
    

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
    line=0
    while True:  
        if(line==20):
            line=0
        else:
            line+=1
        testarr=str(round(random.uniform(-1, 1), 2))+"N"+str(round(random.uniform(-1, 1), 2))
        # testarr = str(line)+"N"+str(line)
        time.sleep(0.016)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
        # 发送数据包
        c.send((testarr).encode("utf-8"))  
        # c.send(('server test, time=' + timestamp).encode("utf-8"))  
        logger.debug(testarr+"\n"+"server send finish time=" + timestamp) 
        
# def receive_message(c: socket):  
#     while True:  
#         recv_data = c.recv(1024)  
#         if recv_data and len(recv_data) > 0:  
#             logger.info(f"receive client message: " + recv_data.decode("utf-8"))  
  
  
if __name__ == "__main__":  
    c = None  
    try:  
        c = main()  
        t_send = threading.Thread(target=send_message, args=(c,))
        t_send.start()  
    except KeyboardInterrupt:  
        if c and type(c) == socket:  
            c.close()  