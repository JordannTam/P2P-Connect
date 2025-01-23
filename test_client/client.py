#coding: utf-8
from socket import *
import sys, threading



# python3 client.py server_IP server_port client_udp_server_port
# 

def P2P(client_udp_port):
    p2pSock = socket(AF_INET, SOCK_DGRAM)
    hostname = gethostname()
    udpclientip = gethostbyname(hostname)
    p2pSock.bind((udpclientip, int(client_udp_port)))

    while True:
        data, addr = p2pSock.recvfrom(1024)
        if data.decode('utf-8') == "**STOP_THREADING**":
            p2pSock.close()
            break
        filename, deviceName, fromDevice = data.decode('utf-8').split(" ")
        content = b""
        while True:
            data, addr = p2pSock.recvfrom(1024)
            if data == b"EndOfFile":
                break
            content += data
        new_filename = f"{deviceName}_{filename}"
        with open(new_filename, "wb") as f:
            f.write(content)
        print(f"Received {filename} from {fromDevice}")


def client():
        server_IP = sys.argv[1]
        server_port = int(sys.argv[2])
        client_udp_port = sys.argv[3]
        hostname = gethostname()
        clientIp = gethostbyname(hostname)

        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((server_IP, server_port))

        clientSocket.send(f"{clientIp} {client_udp_port}".encode("utf-8"))

        t1 = threading.Thread(target=P2P, args=[client_udp_port])
        t1.start()

        while True:
            responseFromServer = clientSocket.recv(1024).decode("utf-8")
            if responseFromServer == "REQUEST":
                userInput = input()
                clientSocket.sendall(userInput.encode("utf-8"))
                if userInput == "OUT":
                    responseFromServer = clientSocket.recv(1024).decode("utf-8")
                    print(responseFromServer, end="")
                    UDPSocket = socket(AF_INET, SOCK_DGRAM)
                    UDPSocket.sendto("**STOP_THREADING**".encode("utf-8"), (clientIp, int(client_udp_port)))
                    break
                continue

            if responseFromServer == "Start_UVF":
                clientSocket.sendall("OK".encode("utf-8"))
                data = clientSocket.recv(1024).decode("utf-8")
                clientSocket.sendall("OK".encode("utf-8"))
                IPaddress, UVFport, filename, deviceName, username = data.split(" ")
                UVFport = int(UVFport)
                UVFSocket = socket(AF_INET, SOCK_DGRAM)
                with open(filename, "rb") as f:
                    file_content = f.read()
                UVFSocket.sendto(f"{filename} {deviceName} {username}".encode("utf-8"), (IPaddress, UVFport))
                while len(file_content) > 1024:
                    send_content = file_content[:1024]
                    UVFSocket.sendto(send_content, (IPaddress, UVFport))
                    file_content = file_content[1024:]

                UVFSocket.sendto(file_content, (IPaddress, UVFport))
                UVFSocket.sendto(b"EndOfFile", (IPaddress, UVFport))
                print(f"{filename} has been uploaded")
                UVFSocket.close()
                continue
            if responseFromServer == "USERNAME_LOCKED":
                clientSocket.sendall("OK".encode("utf-8"))
                UDPSocket = socket(AF_INET, SOCK_DGRAM)
                UDPSocket.sendto("**STOP_THREADING**".encode("utf-8"), (clientIp, int(client_udp_port)))
                break
            print(responseFromServer, end="")
            clientSocket.sendall("OK".encode("utf-8"))
        clientSocket.close()

if __name__ == "__main__":
    client()
#and close the socket
