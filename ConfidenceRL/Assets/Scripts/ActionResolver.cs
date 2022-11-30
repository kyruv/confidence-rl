using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ActionResolver : MonoBehaviour
{
    private CharacterController _controller;
    private float _playerSpeed = 12.0f;
    private float _rotationSpeed = 360;


    private float locked_y_position;
    private Vector3 right = new Vector3(0, 1, 0);
    private Vector3 left = new Vector3(0, -1, 0);
    private Vector3 forward = new Vector3(0, -1, 0);

    void Start()
    {
        _controller = gameObject.AddComponent<CharacterController>();
        locked_y_position = transform.position.y;
    }

    public void DoAction(Action a)
    {
        switch (a)
        {
            case Action.ROTATE_RIGHT:
                transform.eulerAngles += right * _rotationSpeed * Time.fixedDeltaTime;
                break;
            case Action.ROTATE_LEFT:
                transform.eulerAngles += left * _rotationSpeed * Time.fixedDeltaTime;
                break;
            case Action.FORWARD:
                _controller.Move(transform.TransformDirection(forward) * _playerSpeed * Time.fixedDeltaTime);
                break;
            case Action.RESET:
                float x = Random.Range(5, 95.0f);
                float z = Random.Range(5, 95.0f);
                float rotation = Random.Range(0f, 360f);
                transform.position = new Vector3(x, transform.position.y, z);
                transform.eulerAngles = new Vector3(0, rotation, 90);
                Physics.SyncTransforms();
                _controller.Move(forward * Time.fixedDeltaTime);
                break;
        }

        Vector3 pos = transform.position;
        pos.y = locked_y_position;
        transform.position = pos;
    }
}

public enum Action
{
    ROTATE_RIGHT = 0,
    ROTATE_LEFT = 1,
    FORWARD = 2,
    RESET = 3,
    CONTROL_TOGGLE = 4,
};
