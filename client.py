'''
Student Name: Denish Maharjan
Assigned Date: 2024-07-01
Submission Date: 2024-08-18
Coursework 2 Title: TCP Chatting System (Client Side Implementation)
'''
#!/usr/bin/env python3
import socket
import threading
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def banner():
    banner_text = [
        Fore.RED + "                                                         ",
        Fore.GREEN + " ,-----.,--.               ,--.    ,--.                 ",
        Fore.YELLOW + "'  .--./|  ,---.  ,--,--.,-'  '-.,-'  '-. ,---. ,--.--. ",
        Fore.BLUE + "|  |    |  .-.  |' ,-.  |'-.  .-''-.  .-'| .-. :|  .--' ",
        Fore.MAGENTA + "'  '--'\\|  | |  |\\ '-'  |  |  |    |  |  \\   --.|  |    ",
        Fore.CYAN + " `-----'`--' `--' `--`--'  `--'    `--'   `----'`--'    ",
        "                                                         ",
        "                                                         ",
        Fore.YELLOW + "                                         By Denish Maharjan"
    ]

    for line in banner_text:
        print(line)
    print(Style.RESET_ALL)

# Call the function to display the banner
banner()
print()

# Taking the nickname from the user
nickname = input("Choose a name: ")

# For admin, prompt for password
if nickname == 'admin':
    password = input("Enter the password: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a socket object
client.connect(('127.0.0.1', 55555))  # Connecting to the server

stop_thread = False

def receive():
    """Handles receiving messages from the server."""
    global stop_thread
    while not stop_thread:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASSWORD':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'Wrong Password!':
                        print("Can't connect. Password Incorrect!")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('You are BANNED and CANNOT join the chat!!!')
                    client.close()
                    stop_thread = True
            elif message.startswith('/serverclosed'):
                print("Server closed. Disconnecting...")
                client.close()
                stop_thread = True
            elif message.startswith('You were kicked'):
                print(message)  # Display kick message
                client.close()
                stop_thread = True
            else:
                print(message)
        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break

def write():
    """Handles sending messages to the server."""
    global stop_thread
    while not stop_thread:
        try:
            message = input("")
            if message.strip() == '/leave':
                client.send(message.encode('ascii'))
                print("Leaving the chat...")
                stop_thread = True
            elif message.startswith('/'):
                if nickname == 'admin':
                    if message.startswith('/kick'):
                        client.send(f'KICK {message[6:]}'.encode('ascii'))
                    elif message.startswith('/ban'):
                        client.send(f'BAN {message[5:]}'.encode('ascii'))
                    elif message.strip() == '/close':
                        client.send('/close'.encode('ascii'))  # Command to close the server
                        stop_thread = True
                else:
                    print("Commands can only be executed by the admin.")
            else:
                client.send(f'{nickname}: {message}'.encode('ascii'))
        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break

# Thread for receiving messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Thread for writing messages
write_thread = threading.Thread(target=write)
write_thread.start()

# Handling disconnection message from server
try:
    while not stop_thread:
        pass
except KeyboardInterrupt:
    print("\nClosing the chat...")
finally:
    stop_thread = True
    client.close()
