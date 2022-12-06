using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Perception : MonoBehaviour
{
    private float tennisballx = 0;
    private float tennisbally = 0;

    public bool onSameCellAsTennisBall = false;

    // Start is called before the first frame update
    void Start()
    {
        GameObject tennisball = GameObject.Find("TennisBall");
        tennisballx = tennisball.transform.position.x;
        tennisbally = tennisball.transform.position.z;
    }

    public List<float> GetPerception()
    {
        // Left distance, Left object, Left confidence, Forward distance, ...
        List<float> perceptions = new List<float>();

        Vector3 origin = new Vector3(transform.position.x, .75f, transform.position.z);

        if (onSameCellAsTennisBall)
        {
            perceptions.Add(1);
        } else
        {
            perceptions.Add(0);
        }

        perceptions.Add(transform.position.x);
        perceptions.Add(transform.position.z);
        perceptions.Add(transform.rotation.y);
        perceptions.Add(tennisballx);
        perceptions.Add(tennisbally);
        return perceptions;
    }
}
