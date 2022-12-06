﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ManualMovement : MonoBehaviour
{
    private RLConnection _rlConnection;

    // Start is called before the first frame update
    void Start()
    {
        _rlConnection = GetComponent<RLConnection>();
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown("w"))
        {
            _rlConnection.QueueAction(Action.FORWARD);
        }
        else if(Input.GetKeyDown("a"))
        {
            _rlConnection.QueueAction(Action.ROTATE_LEFT);
        } else if(Input.GetKeyDown("d"))
        {
            _rlConnection.QueueAction(Action.ROTATE_RIGHT);
        }
        else if(Input.GetKeyDown("s"))
        {
            _rlConnection.QueueAction(Action.RESET);
        }
    }
}
