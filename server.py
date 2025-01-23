#coding: utf-8
from socket import *
import sys, re, os, threading, time, datetime
#using the socket module

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
# change this port number if required


auth_data = {}
devices_count = 0

def send_message(cs, content):
    cs.sendall(content.encode("utf-8"))
    cs.recv(1024).decode("utf-8")
    

def get_response(cs):
    cs.sendall("REQUEST".encode("utf-8"))
    return cs.recv(1024).decode("utf-8")


def lock_account(username):
    print(f"{username} is locked for 10secs")
    auth_data[username]["lock"] = True
    time.sleep(10)
    auth_data[username]["lock"] = False


def newClient(cs, addr):
    global devices_count
    devices_count += 1
    count = 1
    username = ""
    password = ""
    data = cs.recv(1024).decode("utf-8")
    clientIP, client_udp_port = data.split(" ")

    while True:
        send_message(cs, "Username: ")
        username = get_response(cs)
        send_message(cs, "Password: ")
        password = get_response(cs)

        if username not in auth_data:
            send_message(cs, "Invalid Username. Please try again\n")
            count += 1
            continue
        elif auth_data[username]["password"] != password:
            if auth_data[username]["lock"]:
                send_message(cs, "Your account is blocked due to multiple authentication failures. Please try again later\n")
                send_message(cs, "USERNAME_LOCKED")
                time.sleep(0.00000001)
                return
            while auth_data[username]["password"] != password:
                if count == number_of_consecutive_failed_attempts:
                    send_message(cs, "Invalid Password. Your account has been blocked. Please try again later\n")
                    send_message(cs, "USERNAME_LOCKED")
                    t1 = threading.Thread(target=lock_account, args=[username])
                    t1.start()
                    time.sleep(0.00000001)
                    return
                send_message(cs, "Invalid Password. Please try again\n")
                send_message(cs, "Password: ")
                password = get_response(cs)
                count += 1
            send_message(cs, "Welcome!\n")
            break
        else:
            if auth_data[username]["lock"]:
                send_message(cs, "Your account is blocked due to multiple authentication failures. Please try again later\n")
                send_message(cs, "USERNAME_LOCKED")
                time.sleep(0.00000001)
                return
            send_message(cs, "Welcome!\n")
            break


    timestamp = datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")

    with open("edge-device-log.txt", "a") as f:
        f.write(f"{devices_count}; {timestamp}; {username}; {clientIP}; {client_udp_port}\n")

    while True:
        send_message(cs, "Enter one of the following commands (EDG, UED, SCS, DTE, AED, OUT, UVF): ")
        response = get_response(cs)
        command = ""
        if response != "":
            arguments = response.split(" ")
            command = arguments[0]

        if command == "EDG":
            print(f"Edge device {username} issued EDG command")
            if len(arguments) != 3:
                send_message(cs, "EDG command requires fileID and dataAmount as arguments.\n")
                continue
            try:
                fileID = int(arguments[1])
                dataAmount = int(arguments[2])
                EDG(cs, username, fileID, dataAmount)
            except:
                send_message(cs, "The fileID or dataAmount are not integers, you need to specify the parameter as integers\n")

        elif command == "UED":
            print(f"Edge device {username} issued UED command")

            if len(arguments) != 2:
                send_message(cs, "UED command requires fileID as argument.\n")
                continue
            # try:
            fileID = int(arguments[1])
            UED(cs, username, fileID)
            # except:
            #     send_message(cs, "The fileID is not an integer, you need to specify the parameter as integers\n")


        elif command == "SCS":
            print(f"Edge device {username} issued SCS command")

            if len(arguments) != 3:
                send_message(cs, "SCS command requires fileID and computationOperation as arguments.\n")
                continue
            try:
                fileID = int(arguments[1])
                computationOperation = arguments[2]
                SCS(cs, username, fileID, computationOperation)
            except:
                send_message(cs, "The fileID is not an integer, you need to specify the parameter as integers\n")

        elif command == "DTE":
            print(f"Edge device {username} issued DTE command")
            if len(arguments) != 2:
                send_message(cs, "DTE command requires fileID as argument.\n")
                continue
            try:
                fileID = int(arguments[1])
                DTE(cs, username, fileID)
            except:
                send_message(cs, "The fileID is not an integer, you need to specify the parameter as integers\n")
        elif command == "AED":
            print(f"Edge device {username} issued AED command")
            AED(cs, username)
        elif command == "UVF":
            print(f"Edge device {username} issued UVF command")
            if len(arguments) != 3:
                send_message(cs, "UVF command requires deviceName and fileName as arguments.\n")
                continue
            deviceName = arguments[1]
            fileName = arguments[2]
            UVF(cs, username, deviceName, fileName)

        elif command == "OUT":
            OUT(cs, username)
            break
        else:
            send_message(cs, "Error. Invalid command!\n")

def EDG(cs, username, fileID, dataAmount):
    send_message(cs, "EDG")
    filename = f"{username}-{fileID}.txt"
    send_message(cs, f"{filename} {dataAmount}")


def SCS(cs, username, fileID, computationOperation):
    filename = f"{username}-{fileID}.txt"
    computationOperations = ["SUM", "AVERAGE", "MAX", "MIN"]
    if not os.path.exists(filename):
        send_message(cs, "The file does not exist at the server side\n")
        return
    if computationOperation not in computationOperations:
        send_message(cs, "Computation Operation is invalid\n")
        return

    lineNumber = 0
    datas = []
    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line != "":
                lineNumber += 1
                datas.append(int(line))
    
    if computationOperation == "SUM":
        result = sum(datas)
    if computationOperation == "AVERAGE":
        result = sum(datas) / lineNumber
    if computationOperation == "MAX":
        result = max(datas)
    if computationOperation == "MIN":
        result = min(datas)
    send_message(cs, f"Computation {computationOperation} result on the file (ID:{fileID}) returned from the server is {str(result)}\n")


def DTE(cs, username, fileID):
    filename = f"{username}-{fileID}.txt"
    if not os.path.exists(filename):
        send_message(cs, "The file does not exist at the server side\n")
        return
    lineNumber = 0
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if line != "":
                lineNumber += 1

    os.remove(filename)
    timestamp = datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")
    line = f"{username}; {timestamp}; {fileID}; {lineNumber}\n"
    with open("deletion-log.txt", "a+") as f:
        f.write(line)
    send_message(cs, f"File with ID of {fileID} has been successfully removed from the central server\n")

def UED(cs, username, fileID):
    send_message(cs, "UED")
    filename = f"{username}-{fileID}.txt"
    send_message(cs, filename)
    cs.sendall("OK".encode("utf-8"))
    response = cs.recv(1024).decode("utf-8")
    cs.sendall("OK".encode("utf-8"))

    if response == "NON-EXIST":
        cs.recv(1024).decode("utf-8")
        return


    content = cs.recv(1024).decode("utf-8")

    with open(filename, "w") as f:
        f.write(content)

    dataAmount = len(content)
    timestamp = datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")
    
    line = f"{username}; {timestamp}; {fileID}; {dataAmount}\n"

    with open("upload-log.txt", "a+") as f:
        f.write(line)
    send_message(cs, f"File {filename} uploaded successfully\n")
    

def AED(cs, username):
    content = ""
    with open("edge-device-log.txt", "r") as f:
        content = ""
        for line in f.readlines():
            elements = line.strip().split(";")
            elements = [x.strip() for x in elements]
            if len(elements) == 5:
                if elements[2] != f"{username}":
                    newline = f"{elements[2]}; {elements[3]}; {elements[4]}; active since {elements[1]}.\n"
                    content += newline
    if content == "":
        send_message(cs, "No active device\n")
    else:
        send_message(cs, content)


def OUT(cs, username):
    device_sequence = 1
    with open("edge-device-log.txt", "r") as f:
        lines = f.readlines()
    with open("edge-device-log.txt", "w") as f:
        for line in lines:
            elements = line.strip().split(";")
            if elements[2] != f" {username}":
                elements[0] = str(device_sequence)
                new_line = ";".join(elements)
                f.write(new_line + '\n')
                device_sequence += 1
    global devices_count
    devices_count -= 1
    print(f"{username} exited the edge network")
    send_message(cs, f"Bye, {username}!\n")


def UVF(cs, username, deviceName, fileName):

    targetDevice = []
    with open("edge-device-log.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line != "":
                elements = line.split(";")
                elements = [x.strip() for x in elements]
                if elements[2] == deviceName:
                    targetDevice = elements
    if not targetDevice:
        send_message(cs, f"{deviceName} is currently not active\n")
        return
    send_message(cs, "Start_UVF")
    send_message(cs, f"{targetDevice[3]} {targetDevice[4]} {fileName} {deviceName} {username}")




if __name__ == "__main__":

    with open("credentials.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            data = line.split(" ")
            auth_data[data[0]] = {
                "password": data[1],
                "lock": False
            }
    with open("edge-device-log.txt", "w") as f:
        pass
    serverPort = int(sys.argv[1])
    number_of_consecutive_failed_attempts = int(sys.argv[2])

    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.settimeout(600)
    #This line creates the server’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4.The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM).

    serverSocket.bind(("localhost", serverPort))
    #The above line binds (that is, assigns) the port number 12000 to the server’s socket. In this manner, when anyone sends a packet to port 12000 at the IP address of the server (localhost in this case), that packet will be directed to this socket.

    serverSocket.listen(1)
    #The serverSocket then goes in the listen state to listen for client connection requests. 


    while 1:
        connectionSocket, addr = serverSocket.accept()
        print("Connected: ", addr)
        threading.Thread(target=newClient, args=(connectionSocket, addr)).start()
        # newClient(connectionSocket, addr)




    connectionSocket.close()
    #close the connectionSocket. Note that the serverSocket is still alive waiting for new clients to connect, we are only closing the connectionSocket.

