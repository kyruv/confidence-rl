using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class StepResolver : MonoBehaviour
{
    private Perception _perception;
    private ActionResolver _actionResolver;

    // Start is called before the first frame update
    void Start()
    {
        _perception = GetComponent<Perception>();
        _actionResolver = GetComponent<ActionResolver>();
    }

    public List<float> Step(Action a)
    {
        _actionResolver.DoAction(a);
        return _perception.GetPerception();
    }
}
