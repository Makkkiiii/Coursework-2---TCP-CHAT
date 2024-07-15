#!/usr/bin/env python3
'''
    Student Name: Denish Maharjan
    Assigned Date: 2024-07-01
    Submission Date: 2024-08-18
    Coursework 2 Title: TCP Chatting System (Server Side Implementation).

'''

#!/usr/bin/env python3
import socket 
import threading
import os

HOST = '127.0.0.1'  # Localhost
PORT = 55555  # Port number
ADMIN_PASSWORD = 'adminpass'  # Admin password for authentication

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a socket object.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the socket
server.bind((HOST, PORT))  # Binding the server to the host and port.
server.listen()  # Listening for incoming connections.

clients = []  # List to store the clients.
nicknames = []  # List to store the nicknames.


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if not msg:
                break
            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('REFUSED to connect!'.encode('ascii'))
                    
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    broadcast(f'{name_to_ban} got BANNED!'.encode('ascii'))  # Notify clients of ban
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} got BANNED!')
                    pass
                else:
                    client.send('REFUSED to connect!'.encode('ascii'))
            elif msg.decode('ascii').strip() == '/leave':
                index = clients.index(client)
                nickname = nicknames[index]
                clients.remove(client)
                client.close()
                nicknames.remove(nickname)
                broadcast(f'{nickname} left the chat!'.encode('ascii'))
                break
            elif msg.decode('ascii').strip() == '/close':
                if nicknames[clients.index(client)] == 'admin':
                    broadcast('Server is closing. Goodbye all!'.encode('ascii'))
                    break
                else:
                    client.send('Only admin can close the server.'.encode('ascii'))
            else:  
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
    try:
        # Check if bans.txt exists, create it if not
        if not os.path.exists('bans.txt'):
            with open('bans.txt', 'w'):
                pass  # Create an empty bans.txt file
        
        while True:
            client, address = server.accept()
            print(f"Connected with {str(address)}")

            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            
            with open('bans.txt', 'r') as f:
                bans = f.readlines()
                
            if nickname + '\n' in bans:
                client.send('BAN'.encode('ascii'))
                client.close()
                continue
            
            if nickname == 'admin':
                client.send('PASSWORD'.encode('ascii'))
                password = client.recv(1024).decode('ascii')
                
                if password != ADMIN_PASSWORD:
                    client.send('Wrong Password!'.encode('ascii'))
                    client.close()
                    continue
            
            nicknames.append(nickname)
            clients.append(client)

            print(f"Nickname of the client is {nickname}")
            broadcast(f"{nickname} joined the chat!".encode('ascii'))
            client.send('Connected to the server!'.encode('ascii'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
    
    except Exception as e:
        print(f"Error occurred: {e}")
        server.close()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by ADMIN.'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by ADMIN.'.encode('ascii'))

if __name__ == '__main__':
    try:
        print("Server is running...")
        print(f'Waiting for Connection ON {HOST}:{PORT}')
        receive()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print("Closing server...")
        for client in clients:
            client.send('/serverclosed'.encode('ascii'))
            client.close()
        server.close()

