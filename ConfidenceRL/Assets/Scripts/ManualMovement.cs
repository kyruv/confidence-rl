using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ManualMovement : MonoBehaviour
{
    private RLConnection _rlConnection;

    private float _moveDelay = 0f;
    private float _elapsedTime = 0f;

    // Start is called before the first frame update
    void Start()
    {
        _rlConnection = GetComponent<RLConnection>();
    }

    public void SetMoveDelay(float f){
        _moveDelay = f;
        _elapsedTime = 0f;
    }

    // Update is called once per frame
    void Update()
    {
        if(_elapsedTime < _moveDelay){
            _elapsedTime += Time.deltaTime;
            return;
        }

        if (Input.GetKeyDown("w"))
        {
            _rlConnection.SubmitHumanMove(Action.FORWARD);
            _elapsedTime = 0;
        }
        else if(Input.GetKeyDown("a"))
        {
            _rlConnection.SubmitHumanMove(Action.ROTATE_LEFT);
            _elapsedTime = 0;
        } else if(Input.GetKeyDown("d"))
        {
            _rlConnection.SubmitHumanMove(Action.ROTATE_RIGHT);
            _elapsedTime = 0;
        }
        else if(Input.GetKeyDown("r"))
        {
            _rlConnection.SubmitHumanMove(Action.RESET);
            _elapsedTime = 0;
        }
    }
}
