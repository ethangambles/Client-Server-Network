import socket
import os
import threading
import time


IP = "" #Replace with IP address of desired connection

PORT = 4890 #replace with open port of desired connection
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
CLIENT_DATA_PATH = r"client_0_data" 

m1 = False
m1time = 0
m1rate = 0
totalSize = 0

def Connect():
    data = input("Enter IP address and port number seperated by space:")
    data = data.split(" ")
    ip = data[0]
    port = int(data[1])
    addr = (ip, port)
    return addr

def Upload(client: socket.socket, data, t0):
    #function for uploading file to server
    cmd = data[0]
    filename = data[1]

    files = os.listdir(CLIENT_DATA_PATH) #all files in directory
    #if the file is in directory, read it and upload it
    if filename in files:
        send_data = f"{cmd}*{filename}*{t0}"
        client.sendall(send_data.encode(FORMAT))

    #if not in directory, return an error
    else:
        msg = f"ERR*File not found in client database."
        client.sendall(msg.encode(FORMAT))


def DownloadNoDelete(client: socket.socket, data):
    name, fileSize = data[1], data[2]
    time = data[3]
    #create file and write to it
    filepath = os.path.join(CLIENT_DATA_PATH, name)
    msg = f"READY*{name}*{fileSize}"
    client.sendall(msg.encode(FORMAT))
    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = client.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")
    
    if len(data) >= 5:
        totalFileSize = data[4]
        print(totalFileSize)
        msg = f"ACK*{name}*{time}*{totalFileSize}"
        client.sendall(msg.encode(FORMAT))
    #send the acknowlegement to server not to delete the file
    else:
        msg = f"ACK*{name}*{time}*{fileSize}"
        client.sendall(msg.encode(FORMAT))


def DownloadWithDelete(client: socket.socket, data):
    name, fileSize = data[1], data[2]
    t0 = data[3]

    #create file and write to it
    filepath = os.path.join(CLIENT_DATA_PATH, name)
    msg = f"READY*{name}*{fileSize}"
    client.sendall(msg.encode(FORMAT))
    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = client.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")
            
    #send the acknowlegement to server not to delete the file
    msg = f"ACKD*{name}*{t0}*{fileSize}"
    client.sendall(msg.encode(FORMAT))

def Download1(client:socket.socket,data):
    name, fileSize = data[1], data[2] #good name and filesize
    name2 = data[3] #badname
    t0 = data[4]
    totalFileSize = int(data[5])
    global totalSize
    totalSize = totalFileSize
    #create file and write to it
    filepath = os.path.join(CLIENT_DATA_PATH, name)
    msg = f"READY*{name}*{fileSize}"
    client.sendall(msg.encode(FORMAT))
    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = client.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")
            
    #send the acknowlegement to server not to delete the file
    msg = f"ACKD1*{name}*{t0}*{fileSize}*{name2}"
    client.sendall(msg.encode(FORMAT))

def Download3(client:socket.socket, data):
    name, fileSize = data[1], data[2]
    name2, fileSize2 = data[3], data[4]
    t0 = data[5]
    #create file and write to it
    filepath = os.path.join(CLIENT_DATA_PATH, name)
    msg = f"READY*{name}*{fileSize}"
    client.sendall(msg.encode(FORMAT))
    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = client.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")
    #send the acknowlegement to server to delete the file and download the next
    msg = f"ACKD3*{name}*{name2}*{fileSize2}*{t0}"
    client.sendall(msg.encode(FORMAT))


def Request(client: socket.socket, data):
    #function for uploading file to server
    cmd = data[0]
    if len(data) >= 4:
        goodfilename, notfilename = data[1], data[2]
        t0 = data[3]
    files = os.listdir(CLIENT_DATA_PATH) #all files in directory
    #if the file is in directory, read it and upload it
    if len(data) <= 3:
        goodfilename = data[1]
        t0 = data[2]
    if goodfilename in files:
        fileSize = str(os.path.getsize(f"{CLIENT_DATA_PATH}\{goodfilename}"))
        if (len(data) <= 3):
            send_data = f"{cmd}*{goodfilename}*{fileSize}*{t0}"
            client.sendall(send_data.encode(FORMAT))
        else:
            send_data = f"{cmd}*{goodfilename}*{fileSize}*{notfilename}*{t0}"
            client.sendall(send_data.encode(FORMAT))

    #if not in directory, return an error
    else:
        msg = f"ERR*File not found in client or server database."
        client.sendall(msg.encode(FORMAT))

def Finish(client: socket.socket, data):
        cmd = data[0]
        file1, file2 = data[1], data[2]
        fileSize = data[3]
        t0 = data[4]
        msg = f"{cmd}*{file1}*{file2}*{t0}"
        client.sendall(msg.encode(FORMAT))

def ListenForServer(client: socket.socket) -> None:
    #This function listens to the server to respond to any messages sent
    while True:
        data = client.recv(SIZE).decode(FORMAT)
        data = data.split("*")#sever messages split at special char '*'
        cmd = data[0]
        global m1
        if cmd == "DISCONNECTED":
            msg = data[1]
            print(f"[SERVER]: {msg}")
            break

        elif cmd == "DONE":
            global totalSize
            msg = data[1]
            print(f"{msg}")
            if len(data) >=3:
                if m1:
                    fileSize = totalSize
                    m1 = False
                    totalSize = 0
                else:
                    fileSize = int(data[3])
                t0 = float(data[2])
                totalTime = time.time() - t0
                datarate = fileSize / totalTime
                datarate = datarate / 1000000
                print(f"Total time: {totalTime} seconds.")
                print(f"Data Rate: {datarate} MB/sec")

            
        elif cmd == "DOWNLOAD":
            DownloadNoDelete(client,data)

        elif cmd == "DOWNLOADX":
            DownloadWithDelete(client,data)

        elif cmd == "DOWNLOAD3":
            Download3(client,data)

        elif cmd == "DOWNLOAD1":
            Download1(client,data)

        elif cmd == "DOWNLOADM1":
            m1 = True
            file1 = data[1]
            file2 = data[2]
            t0 = data[3]
            client.sendall(f"{cmd}*{file1}*{file2}*{t0}".encode(FORMAT))
        elif cmd == "REQUEST":
            Request(client,data)

        elif cmd == "REQUESTM1":
            Request(client,data)

        elif cmd == "REQUESTM2":
            Request(client,data)

        elif cmd == "REQUESTM3":
            Request(client,data)

        elif cmd == "READY":
            filename = data[1]
            fileSize = str(os.path.getsize(f"{CLIENT_DATA_PATH}\{filename}"))
            client.sendall(fileSize.encode(FORMAT))
            with open(f"{CLIENT_DATA_PATH}\{filename}", "rb") as f:
                for l in f: client.sendall(l)
                f.close()

        elif cmd == "READYD":
            filename = data[1]
            with open(f"{CLIENT_DATA_PATH}\{filename}", "rb") as f:
                for l in f: client.sendall(l)
                f.close()

        elif cmd == "FINISHM2":
            Finish(client,data)

        elif cmd == "FINISHM3":
            Finish(client,data)

def ListenForUser(client: socket.socket) -> None:
    #This function listens to the user terminal input
    while True:
        data = input()
        data = data.split(" ") #user input split at space
        cmd = data[0]

        if cmd == "LOGOUT":
            client.sendall(cmd.encode(FORMAT))
            break

        elif cmd == "DIR":
            client.sendall(cmd.encode(FORMAT))

        elif cmd == "DELETE":
            client.sendall(f"{cmd}*{data[1]}".encode(FORMAT))

        elif cmd == "UPLOAD":
            t0 = time.time()
            Upload(client,data,t0)

        elif cmd == "DOWNLOAD":
            t0 = time.time()
            filename = data[1]
            client.sendall(f"{cmd}*{filename}*{t0}".encode(FORMAT))


        elif cmd == "DOWNLOADM1":
            t0 = time.time()
            file1 = data[1]
            file2 = data[2]
            client.sendall(f"{cmd}*{file1}*{file2}*{t0}".encode(FORMAT))

        elif cmd == "DOWNLOADM2":
            t0 = time.time()
            file1 = data[1]
            file2 = data[2]
            client.sendall(f"{cmd}*{file1}*{file2}*{t0}".encode(FORMAT))

        elif cmd == "DOWNLOADM3":
            t0 = time.time()
            file1 = data[1]
            file2 = data[2]
            client.sendall(f"{cmd}*{file1}*{file2}*{t0}".encode(FORMAT))
        else:
            client.sendall(cmd.encode(FORMAT))

def main():
    #Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = Connect()
    client.connect(addr)

    #create 2 threads for listening to server and user
    server_thread = threading.Thread(target=ListenForServer, args=(client,))
    user_thread = threading.Thread(target=ListenForUser, args=(client,))

    #start threads
    server_thread.start()
    user_thread.start()

    #if threads exit, connection has ended
    server_thread.join()
    user_thread.join()
 
    #disconnect client
    client.close()

if __name__ == "__main__":
    main()