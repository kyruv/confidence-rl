using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;


public class ActionResolver : MonoBehaviour
{
    private float _playerSpeed = 8.0f;
    private float _rotationSpeed = 45;

    private Vector3[,] grid = new Vector3[5, 12];
    private bool[,] validLocations = new bool[5, 12];
    private Vector2 dogRowCol;
    private Dictionary<int, Vector2> directionMovement = new Dictionary<int, Vector2>();

    private float locked_y_position;
    private Vector2 tennisBallRowCol;

    void Start()
    {
        locked_y_position = transform.position.y;

        for (int r =0; r<5; r++)
        {
            for(int c = 0; c < 12; c++)
            {
                grid[r, c] = new Vector3(4.5f + 8f * c, locked_y_position, 4.5f + 8f * r);
                if((r == 1 && c == 1) || (r == 1 && c == 9) || (r == 2 && c == 9) || (r == 2 && c == 10) || (r == 3 && c == 10) || (r==0 && c== 3) || (r == 1 && c == 3) || (r == 3 && c == 3) || (r == 4 && c == 3))
                {
                    validLocations[r, c] = false;
                } else
                {
                    validLocations[r, c] = true;
                }
            }
        }

        directionMovement.Add(0, new Vector2(0, 1));
        directionMovement.Add(45, new Vector2(-1, 1));
        directionMovement.Add(90, new Vector2(-1, 0));
        directionMovement.Add(135, new Vector2(-1, -1));
        directionMovement.Add(180, new Vector2(0, -1));
        directionMovement.Add(225, new Vector2(1, -1));
        directionMovement.Add(270, new Vector2(1, 0));
        directionMovement.Add(315, new Vector2(1, 1));

        tennisBallRowCol = new Vector2(2, 11);
        GameObject.Find("TennisBall").transform.position = grid[2, 11];

        DoAction(Action.RESET);
    }

    public void DoAction(Action a)
    {
        transform.eulerAngles = new Vector3(0, (transform.eulerAngles.y) % 360, 90);
        switch (a)
        {
            case Action.ROTATE_RIGHT:
                transform.eulerAngles = new Vector3(0, (transform.eulerAngles.y + _rotationSpeed) % 360, 90);
                break;
            case Action.ROTATE_LEFT:
                transform.eulerAngles = new Vector3(0, (transform.eulerAngles.y - _rotationSpeed) % 360, 90);
                break;
            case Action.FORWARD:
                Vector2 forwardDir = directionMovement[Mathf.RoundToInt(transform.eulerAngles.y % 360)];

                int potnewr = Mathf.RoundToInt((dogRowCol.x + forwardDir.x));
                int potnewc = Mathf.RoundToInt((dogRowCol.y + forwardDir.y));
                if(potnewr >= 0 && potnewr < 5 && potnewc >=0 && potnewc < 12 && validLocations[potnewr, potnewc])
                {
                    dogRowCol = new Vector2(potnewr, potnewc);
                    transform.position = grid[Mathf.RoundToInt(dogRowCol.x), Mathf.RoundToInt(dogRowCol.y)];
                }

                break;
            case Action.RESET:
                GetComponent<Perception>().onSameCellAsTennisBall = false;

                int r = Random.Range(0, 5);
                int c = Random.Range(0, 12);
                while(!validLocations[r, c]){
                    r = Random.Range(0, 5);
                    c = Random.Range(0, 12);
                }
                
                int rotation = Random.Range(0, 8) * 45;
                transform.position = grid[r, c];
                transform.eulerAngles = new Vector3(0, rotation, 90);

                dogRowCol = new Vector2(r, c);
                break;
        }

        Vector3 pos = transform.position;
        pos.y = locked_y_position;
        transform.position = pos;

        if(tennisBallRowCol == dogRowCol)
        {
            GetComponent<Perception>().onSameCellAsTennisBall = true;
        }
    }
}

public enum Action
{
    ROTATE_RIGHT = 0,
    ROTATE_LEFT = 1,
    FORWARD = 2,
    RESET = 3,
    CONTROL_TOGGLE = 4,
};
