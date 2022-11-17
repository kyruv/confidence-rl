using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ManualMovement : MonoBehaviour
{
    private CharacterController _controller;
    private float _playerSpeed = 4.0f;
    private float _rotationSpeed = 120;

    // Start is called before the first frame update
    void Start()
    {
        _controller = gameObject.AddComponent<CharacterController>();
    }

    // Update is called once per frame
    void Update()
    {
        Vector3 rotation = new Vector3(Input.GetAxisRaw("Horizontal") * _rotationSpeed * Time.deltaTime, 0, 0);

        Vector3 move = new Vector3(0, -Input.GetAxisRaw("Vertical") * Time.deltaTime, 0);
        move = transform.TransformDirection(move);
        _controller.Move(move * _playerSpeed);
        transform.Rotate(rotation);
    }
}
