'''

Student Name: Denish Maharjan
Assigned Date: 2024-07-01
Submission Date: 2024-08-18
Coursework 2 Title: TCP Chatting System (Server Side Implementation).

'''
# Importing the necessary libraries.

#!/usr/bin/env python3
import socket 
import threading

host = '127.0.0.1'  # Localhost
port = 55555  # Port number

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a socket object.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the socket
server.bind((host, port))  # Binding the server to the host and port.
server.listen()  # Listening for incoming connections.

clients = []  # List to store the clients.
nicknames = []  # List to store the nicknames.


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except Exception as e:
            print(f"Exception occurred: {e}")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == '__main__':
    try:
        print("Server is running...")
        print(f'Listening on {host}:{port}')
        receive()
    except Exception as e:
        print(f"Error occurred: {e}")
