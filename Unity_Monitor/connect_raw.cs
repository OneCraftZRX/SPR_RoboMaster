using System;  
using System.Collections;  
using System.Net;  
using System.Net.Sockets;  
using System.Text;  
using System.Threading;  
using UnityEngine;  
  
public class SocketManager : MonoBehaviour  
{  
      
    public string ipAddress = "127.0.0.1";  
    public int port = 7788;  
  
    private Socket clientSocket;  
      
    byte[] _data = new byte[1024];  
  
    private Thread _thread;  
    private string _message;  
  
    private void Start()  
    {  
        ConnectToServer();  
    }  
  
    void ConnectToServer()  
    {  
        clientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);  
        clientSocket.Connect(new IPEndPoint(IPAddress.Parse(ipAddress), port));  
  
        _thread = new Thread(ReceiveMessage);  
        _thread.Start();  
        StartCoroutine(RandomSend());  
    }  
  
    // 启动线程, 持续接收消息  
    void ReceiveMessage()  
    {  
        while (true)  
        {  
            if (clientSocket.Connected == false)  
                break;  
            int length = clientSocket.Receive(_data);  
  
            _message = Encoding.UTF8.GetString(_data, 0, length);  
              
            Debug.Log("receive message: " + _message);  
        }  
    }  
  
  
    // 使用IEnumerator, 每隔2秒发送给server端一次消息  
    IEnumerator RandomSend()  
    {  
        while (true)  
        {  
            SendMessages("client send..." + DateTime.Now);  
            yield return new WaitForSeconds(2f);  
        }  
    }  
  
    void SendMessages(string message)  
    {  
        byte[] data = Encoding.UTF8.GetBytes(message);  
        clientSocket.Send(data);  
    }  
  
    void OnDestroy()  
    {  
        _thread.Abort();  
        clientSocket.Shutdown(SocketShutdown.Both);  //既不接受也不发送  
        clientSocket.Close();  //关闭连接  
    }  
} 