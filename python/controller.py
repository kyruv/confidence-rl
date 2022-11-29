import socket
import keyboard
import time
import gym_envs
import gym
import numpy as np


host = 'localhost' 
port = 50000
backlog = 5 
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((host,port)) 
s.listen(backlog)

human_controlling = False
data = None

while True:
    client, address = s.accept() 
    env = gym.make('UnityEnv-v0', unity_sim_client=client)
    print("Client connected.")

    while True:
        env.reset()
        terminated = False
        total_reward = 0

        while not terminated:
            r = 0
            action = np.random.randint(0,3)
            obs, r, terminated, _, _ = env.step(action)
            total_reward+=r
            print("action: "+str(action) + " -- obs: "+str(obs))


    # while True:
    #     wait_for_response = False
        
    #     if human_controlling:
    #         wait_for_response = True

    #     if not human_controlling and keyboard.is_pressed('w'):
    #         print('forward')
    #         wait_for_response = True
    #         client.send('f'.encode())
    #     elif not human_controlling and keyboard.is_pressed('a'):
    #         print('left')
    #         wait_for_response = True
    #         client.send('l'.encode())
    #     elif not human_controlling and keyboard.is_pressed('d'):
    #         print('right')
    #         wait_for_response = True
    #         client.send('r'.encode())
    #     elif not human_controlling and keyboard.is_pressed('n'):
    #         print('new')
    #         wait_for_response = True
    #         client.send('n'.encode())
    #     elif keyboard.is_pressed('h'):
    #         print('control toggle')
    #         wait_for_response = True
    #         human_controlling = not human_controlling
    #         client.send('h'.encode())
    #     elif keyboard.is_pressed('q'):
    #         print('q')
    #         client.send("Bye!".encode())
    #         client.close()
    #         break
        
    #     if wait_for_response:
    #         data = client.recv(size)
    #         print(data)

    #     if data != None:
    #         perception = data.decode().split(',')
    #         if perception[0] == '1':
    #             client.send('n'.encode())
    #             data = client.recv(size)     