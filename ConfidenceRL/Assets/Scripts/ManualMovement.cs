using System.Collections;
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
        List<float> perception = null;
        if (Input.GetAxisRaw("Horizontal") > 0)
        {
            _rlConnection.QueueAction(Action.ROTATE_RIGHT);
        }
        else if(Input.GetAxisRaw("Horizontal") < 0)
        {
            _rlConnection.QueueAction(Action.ROTATE_LEFT);
        } else if(Input.GetAxisRaw("Vertical") > 0)
        {
            _rlConnection.QueueAction(Action.FORWARD);
        }
    }
}
