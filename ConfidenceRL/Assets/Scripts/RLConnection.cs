using UnityEngine;
using System;
using System.Net.Sockets;
using System.Net;
using System.Collections.Generic;
using System.Linq;
using System.Collections.Concurrent;

public class RLConnection : MonoBehaviour
{
    private StepResolver _step;
    private ConcurrentQueue<Action> _mainThreadActions = new ConcurrentQueue<Action>();

    private Socket _clientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
    private byte[] _recieveBuffer = new byte[8142];

    void Start()
    {
        _step = GetComponent<StepResolver>();
        SetupServer();
    }

    private void Update()
    {
        // Handle all callbacks in main thread
        while (_mainThreadActions.Count > 0 && _mainThreadActions.TryDequeue(out Action action))
        {
            List<float> perception = _step.Step(action);
            SendData(System.Text.Encoding.Default.GetBytes(string.Join(",", perception)));
        }
    }

    void OnApplicationQuit()
    {
        _clientSocket.Close();
    }

    private void SetupServer()
    {
        try
        {
            _clientSocket.Connect(new IPEndPoint(IPAddress.Loopback, 50000));
        }
        catch (SocketException ex)
        {
            Debug.Log(ex.Message);
        }

        _clientSocket.BeginReceive(_recieveBuffer, 0, _recieveBuffer.Length, SocketFlags.None, new AsyncCallback(ReceiveCallback), null);

    }


    private void ReceiveCallback(IAsyncResult AR)
    {
        //Check how much bytes are recieved and call EndRecieve to finalize handshake
        int recieved = _clientSocket.EndReceive(AR);

        if (recieved <= 0)
            return;

        //Copy the recieved data into new buffer , to avoid null bytes
        byte[] recData = new byte[recieved];
        Buffer.BlockCopy(_recieveBuffer, 0, recData, 0, recieved);

        string command = System.Text.Encoding.Default.GetString(_recieveBuffer);
        command = new string(command.Where(c => !char.IsControl(c)).ToArray());
        Debug.Log("command received " + command);

        switch (command)
        {
            case "f":
                _mainThreadActions.Enqueue(Action.FORWARD);
                break;
            case "l":
                _mainThreadActions.Enqueue(Action.ROTATE_LEFT);
                break;
            case "r":
                _mainThreadActions.Enqueue(Action.ROTATE_RIGHT);
                break;
            default:
                Debug.Log("Nothing received " + command);
                break;
        }

        //Start receiving again
        _clientSocket.BeginReceive(_recieveBuffer, 0, _recieveBuffer.Length, SocketFlags.None, new AsyncCallback(ReceiveCallback), null);
    }

    private void SendData(byte[] data)
    {
        SocketAsyncEventArgs socketAsyncData = new SocketAsyncEventArgs();
        socketAsyncData.SetBuffer(data, 0, data.Length);
        _clientSocket.SendAsync(socketAsyncData);
    }
}
