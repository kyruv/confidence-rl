using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ActionResolver : MonoBehaviour
{
    private CharacterController _controller;
    private float _playerSpeed = 4.0f;
    private float _rotationSpeed = 120;

    private Vector3 right = new Vector3(0, 1, 0);
    private Vector3 left = new Vector3(0, -1, 0);
    private Vector3 forward = new Vector3(0, -1, 0);

    void Start()
    {
        _controller = gameObject.AddComponent<CharacterController>();
    }

    public void DoAction(Action a)
    {
        switch (a)
        {
            case Action.ROTATE_RIGHT:
                transform.eulerAngles += right * _rotationSpeed * Time.deltaTime;
                break;
            case Action.ROTATE_LEFT:
                transform.eulerAngles += left * _rotationSpeed * Time.deltaTime;
                break;
            case Action.FORWARD:
                _controller.Move(transform.TransformDirection(forward) * _playerSpeed * Time.deltaTime);
                break;
            case Action.RESET:
                float x = Random.Range(5, 95.0f);
                float z = Random.Range(5, 95.0f);
                float rotation = Random.Range(0f, 360f);
                transform.position = new Vector3(x, transform.position.y, z);
                transform.eulerAngles = new Vector3(0, rotation, 90);
                Physics.SyncTransforms();
                _controller.Move(forward * Time.deltaTime);
                break;
        }
    }
}

public enum Action
{
    ROTATE_RIGHT = 0,
    ROTATE_LEFT = 1,
    FORWARD = 2,
    RESET = 3
};
