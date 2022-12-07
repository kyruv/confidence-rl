using UnityEngine;
using UnityEngine.AI;
using System;
using System.Net.Sockets;
using System.Net;
using System.Collections.Generic;
using System.Linq;
using System.Collections.Concurrent;

public class RLConnection : MonoBehaviour
{
    public bool tellBestMoves;
    public float withinAngle = 15;
    public float closeEnoughDistance = .5f;

    public bool humanControlledAlways = false;

    private NavMeshPath _navMeshPath;
    private Transform _target;
    
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
        _target = GameObject.Find("TennisBall").transform;
        _navMeshPath = new NavMeshPath();
        SetupServer();
    }

    public void SubmitHumanMove(Action a)
    {
        _mainThreadActions.Enqueue(a);
        if (!humanControlledAlways)
        {
            _manualMovement.enabled = false;
            _humanControlledText.SetActive(false);
        }
    }

    private void Update()
    {
        // Handle all callbacks in main thread
        while (_mainThreadActions.Count > 0 && _mainThreadActions.TryDequeue(out Action action))
        {
            print("Doing action "+ action.ToString());
            if(action == Action.HUMAN_MOVE_REQUESTED)
            {
                _manualMovement.enabled = true;
                _humanControlledText.SetActive(true);
                SendData(System.Text.Encoding.Default.GetBytes("ack control handoff"));
                continue;
            }

            List<float> perception = _step.Step(action);

            if (tellBestMoves)
            {
                NavMesh.CalculatePath(transform.position, _target.position, NavMesh.AllAreas, _navMeshPath);

                // Find the waypoint to path towards
                int bestWayPoint = -1;
                for (int i = 1; i < _navMeshPath.corners.Length; i++)
                {
                    if(Vector3.Distance(transform.position, _navMeshPath.corners[i]) > closeEnoughDistance)
                    {
                        bestWayPoint = i;
                        break;
                    } 
                }
                 
                if (bestWayPoint != -1)
                {
                    float move = calcNextMove(_navMeshPath.corners[bestWayPoint]);
                    perception.Add(move);
                } else
                {
                    perception.Add(-1);
                }
            } else
            {
                perception.Add(-1);
            }

            print("Sending " + string.Join(",", perception));
            SendData(System.Text.Encoding.Default.GetBytes(string.Join(",", perception)));
        }
    }

    private static float GetAngleOnAxis(Vector3 self, Vector3 other)
    {
        float angle = Vector3.Angle(self, other);
        Vector3 cross = Vector3.Cross(self, other);
        if (cross.y < 0) angle = -angle;
        return angle;
    }

    private float calcNextMove(Vector3 to)
    {
        Vector3 idealForward = to - transform.position;
        idealForward.y = 0;
        float angle = GetAngleOnAxis(-transform.up, idealForward);
        // print("OFF BY " + angle);

        if(Math.Abs(angle) < withinAngle)
        {
            return 0f;
        }
        else if(angle > 0)
        {
            return 1f;
        }

        return 2f;
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
                _mainThreadActions.Enqueue(Action.HUMAN_MOVE_REQUESTED);
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
