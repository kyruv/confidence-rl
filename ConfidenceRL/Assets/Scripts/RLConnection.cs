using UnityEngine;
using System;
using System.Net.Sockets;
using System.Net;
using System.Collections.Generic;
using System.Linq;
using System.Collections.Concurrent;

public class RLConnection : MonoBehaviour
{
    private GameObject _humanControlledText;
    private ManualMovement _manualMovement;
    private StepResolver _step;
    private ConcurrentQueue<Action> _mainThreadActions = new ConcurrentQueue<Action>();

    private Socket _clientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
    private byte[] _recieveBuffer = new byte[8142];

    void Start()
    {
        _step = GetComponent<StepResolver>();
        _manualMovement = GetComponent<ManualMovement>();
        _humanControlledText = GameObject.Find("HumanControlledText");
        _humanControlledText.SetActive(false);
        SetupServer();
    }

    public void QueueAction(Action a)
    {
        _mainThreadActions.Enqueue(a);
    }

    private void Update()
    {
        // Handle all callbacks in main thread
        while (_mainThreadActions.Count > 0 && _mainThreadActions.TryDequeue(out Action action))
        {
            print("Doing action "+ action.ToString());
            if(action == Action.CONTROL_TOGGLE)
            {
                _manualMovement.enabled = !_manualMovement.enabled;
                _humanControlledText.SetActive(_manualMovement.enabled);
                SendData(System.Text.Encoding.Default.GetBytes("ack control handoff"));
                continue;
            }

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

        // It is possible to receive multiple commands in one packet. It really only should happen with the keyboard input mode. And if it does then we are safe to just ignore extra commands.
        string command = System.Text.Encoding.Default.GetString(_recieveBuffer);
        command = new string(command.Where(c => !char.IsControl(c)).ToArray());
        char[] commands = command.ToCharArray();
        char firstCommand = commands[0];
        switch (firstCommand)
        {
            case 'f':
                _mainThreadActions.Enqueue(Action.FORWARD);
                break;
            case 'l':
                _mainThreadActions.Enqueue(Action.ROTATE_LEFT);
                break;
            case 'r':
                _mainThreadActions.Enqueue(Action.ROTATE_RIGHT);
                break;
            case 'n':
                _mainThreadActions.Enqueue(Action.RESET);
                break;
            case 'h':
                _mainThreadActions.Enqueue(Action.CONTROL_TOGGLE);
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
