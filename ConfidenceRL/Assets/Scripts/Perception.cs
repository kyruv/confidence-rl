using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Perception : MonoBehaviour
{
    private float tennisballx = 0;
    private float tennisbally = 0;

    private ActionResolver actionResolver;

    public bool onSameCellAsTennisBall = false;

    // Start is called before the first frame update
    void Start()
    {
        GameObject tennisball = GameObject.Find("TennisBall");
        tennisballx = tennisball.transform.position.x;
        tennisbally = tennisball.transform.position.z;

        actionResolver = GetComponent<ActionResolver>();
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

        perceptions.Add(Mathf.RoundToInt(actionResolver.dogRowCol.x));
        perceptions.Add(Mathf.RoundToInt(actionResolver.dogRowCol.y));
        perceptions.Add(transform.eulerAngles.y % 360);
        perceptions.Add(Mathf.RoundToInt(actionResolver.tennisBallRowCol.x));
        perceptions.Add(Mathf.RoundToInt(actionResolver.tennisBallRowCol.y));
        return perceptions;
    }
}
