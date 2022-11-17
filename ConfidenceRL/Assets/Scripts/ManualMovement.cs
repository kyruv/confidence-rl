using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ManualMovement : MonoBehaviour
{
    private StepResolver _step;

    // Start is called before the first frame update
    void Start()
    {
        _step = GetComponent<StepResolver>();
    }

    // Update is called once per frame
    void Update()
    {
        List<float> perception = null;
        if (Input.GetAxisRaw("Horizontal") > 0)
        {
            perception = _step.Step(Action.ROTATE_RIGHT);
        }
        else if(Input.GetAxisRaw("Horizontal") < 0)
        {
            perception = _step.Step(Action.ROTATE_LEFT);
        } else if(Input.GetAxisRaw("Vertical") > 0)
        {
            perception = _step.Step(Action.FORWARD);
        }
        if(perception != null && perception[0] == 1f)
        {
            _step.Step(Action.RESET);
        }
    }
}
