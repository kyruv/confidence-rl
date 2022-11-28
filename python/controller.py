import socket
import json
import keyboard

host = 'localhost' 
port = 50000
backlog = 5 
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((host,port)) 
s.listen(backlog) 

while True:
    client, address = s.accept() 
    print("Client connected.")
    while 1:
        key_pressed = False
        if keyboard.is_pressed('w'):
            print('forward')
            key_pressed = True
            client.send('f'.encode())
        elif keyboard.is_pressed('a'):
            print('left')
            key_pressed = True
            client.send('l'.encode())
        elif keyboard.is_pressed('d'):
            print('right')
            key_pressed = True
            client.send('r'.encode())
        elif keyboard.is_pressed('n'):
            print('new')
            key_pressed = True
            client.send('n'.encode())
        elif keyboard.is_pressed('q'):
            print('q')
            client.send("Bye!".encode())
            client.close()
            break
        
        if key_pressed:
            data = client.recv(size)
            print(data)