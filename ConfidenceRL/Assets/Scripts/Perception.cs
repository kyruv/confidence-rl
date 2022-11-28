using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Perception : MonoBehaviour
{
    private Camera frontCamera;
    private Camera leftCamera;
    private Camera rightCamera;

    private Dictionary<string, Vector3> rayCastDirections = new Dictionary<string, Vector3>();
    private Dictionary<string, float> tagMapping = new Dictionary<string, float>();

    private bool isTouchingTennisball;


    // Start is called before the first frame update
    void Start()
    {
        rayCastDirections.Add("forward", Vector3.down);
        rayCastDirections.Add("right", Vector3.back);
        rayCastDirections.Add("left", Vector3.forward);

        tagMapping.Add("obstacle", 0f);
        tagMapping.Add("tennisball", 1f);

        frontCamera = GameObject.Find("FrontCamera").GetComponent<Camera>();
        leftCamera = GameObject.Find("LeftCamera").GetComponent<Camera>();
        rightCamera = GameObject.Find("RightCamera").GetComponent<Camera>();
    }

    void OnTriggerEnter(Collider other)
    {
        if(other.gameObject.tag == "tennisball")
        {
            isTouchingTennisball = true;
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.gameObject.tag == "tennisball")
        {
            isTouchingTennisball = false;
        }
    }

    public List<float> GetPerception()
    {
        // Left distance, Left object, Left confidence, Forward distance, ...
        List<float> perceptions = new List<float>();

        // don't collide with the dog itself
        int layerMask = 1 << 8;
        layerMask = ~layerMask;

        Vector3 origin = new Vector3(transform.position.x, .75f, transform.position.z);

        if (isTouchingTennisball)
        {
            perceptions.Add(1f);
        } else
        {
            perceptions.Add(0f);
        }

        perceptions.Add(transform.position.x);
        perceptions.Add(transform.position.z);

        RaycastHit hit;
        if (Physics.Raycast(origin, transform.TransformDirection(rayCastDirections["left"]), out hit, 200f, layerMask))
        {
            Debug.DrawRay(origin, transform.TransformDirection(rayCastDirections["left"]) * hit.distance, Color.yellow);
            perceptions.Add(hit.distance);
            perceptions.Add(tagMapping[hit.transform.gameObject.tag]);
            perceptions.Add(1f);
        }

        if (Physics.Raycast(origin, transform.TransformDirection(rayCastDirections["forward"]), out hit, 200f, layerMask))
        {
            Debug.DrawRay(origin, transform.TransformDirection(rayCastDirections["forward"]) * hit.distance, Color.yellow);
            perceptions.Add(hit.distance);
            perceptions.Add(tagMapping[hit.transform.gameObject.tag]);
            perceptions.Add(1f);
        }

        if (Physics.Raycast(origin, transform.TransformDirection(rayCastDirections["right"]), out hit, 200f, layerMask))
        {
            Debug.DrawRay(origin, transform.TransformDirection(rayCastDirections["right"]) * hit.distance, Color.yellow);
            perceptions.Add(hit.distance);
            perceptions.Add(tagMapping[hit.transform.gameObject.tag]);
            perceptions.Add(1f);
        }
        return perceptions;
    }
}
