import os
import socket
import threading
import datetime
import time
import pathlib

IP = socket.gethostbyname(socket.gethostname())
PORT = 4890
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = r"server_data"
ADDRESSES = []
CONNECTIONS = []
DOWNLOADS = {}
DELETEME = []
FILENAMES = []
numDeletes = -1
totalFileSize = 0

m1 = False

#Dowload function
def download(conn: socket.socket, addr, filename, t0):
    global totalFileSize
    files = os.listdir(SERVER_PATH)
    msg = "DONE*"
    #File if requested file in server dir
    if filename in files:

        fileSize = str(os.path.getsize(f"{SERVER_PATH}\{filename}"))
        if totalFileSize != 0:
            send_data = f"DOWNLOAD*{filename}*{fileSize}*{t0}*{totalFileSize}"
            conn.sendall(send_data.encode(FORMAT))

        else:
            send_data = f"DOWNLOAD*{filename}*{fileSize}*{t0}"
            conn.sendall(send_data.encode(FORMAT))
        if filename not in DOWNLOADS:
            DOWNLOADS[filename] = 0
                
    else:
        if(addr == ADDRESSES[0]):
            #upload from ADDRESSES[1]
            send_data = f"REQUEST*{filename}*{t0}"
            CONNECTIONS[1].sendall(send_data.encode(FORMAT))
            msg += "Requesting file"

        else:
            #upload from ADDRESSES[0]
            send_data = f"REQUEST*{filename}*{t0}"
            CONNECTIONS[0].sendall(send_data.encode(FORMAT))
            msg += "Requesting file"

def downloadfirstm1(conn:socket.socket, addr, goodfilename, t0, badfilename):
    global totalFileSize
    files = os.listdir(SERVER_PATH)
    msg = "DONE*"
    print(f"downloadingm1 {goodfilename}")
    #File if requested file in server dir
    if goodfilename not in DOWNLOADS:
        DOWNLOADS[goodfilename] = 0
    if(addr == ADDRESSES[0]):
        #upload from ADDRESSES[1]
        send_data = f"REQUESTM1*{goodfilename}*{badfilename}*{t0}"
        CONNECTIONS[1].sendall(send_data.encode(FORMAT))
        msg += "Requesting file"

    else:
        #upload from ADDRESSES[0]
        send_data = f"REQUESTM1*{goodfilename}*{badfilename}*{t0}"
        CONNECTIONS[0].sendall(send_data.encode(FORMAT))
        msg += "Requesting file"


#Download function multiple strategy 1      
def downloadm1(conn: socket.socket, addr, recieved):
    filename1 = recieved[1]
    filename2 = recieved[2]
    t0 = recieved[3]
    global m1
    files = os.listdir(SERVER_PATH)
    if m1:
        #second run
        if filename1 in FILENAMES:
            download(conn, addr, filename2, t0)
        else:
            download(conn, addr, filename1, t0)
        m1 = False
    else:
        #first run
        if filename1 in files:
            downloadfirstm1(conn, addr, filename2, t0, filename1)
        else:
            downloadfirstm1(conn, addr, filename1, t0, filename2)
    global totalFileSize
    totalFileSize = 0


#Download function multiple strategy 2
def downloadm2(conn: socket.socket, addr, recieved):
    filename1 = recieved[1]
    filename2 = recieved[2]
    t0 = recieved[3]
    files = os.listdir(SERVER_PATH)

    if filename1 not in DOWNLOADS:
         DOWNLOADS[filename1] = 0

    if  filename2 not in DOWNLOADS:
        DOWNLOADS[filename2] = 0

    if filename1 not in files:        
        DELETEME.append(filename1)
        global numDeletes
        numDeletes += 1

        if(addr == ADDRESSES[0]):
            #upload from ADDRESSES[1]
            send_data = f"REQUESTM2*{filename1}*{filename2}*{t0}"
            CONNECTIONS[1].sendall(send_data.encode(FORMAT))
            

        else:
            #upload from ADDRESSES[0]
            send_data = f"REQUESTM2*{filename1}*{filename2}*{t0}"
            CONNECTIONS[0].sendall(send_data.encode(FORMAT))
            

    if filename2 not in files:
        DELETEME.append(filename2) 
        numDeletes += 1
        if(addr == ADDRESSES[0]):
            #upload from ADDRESSES[1]
            send_data = f"REQUESTM2*{filename2}*{filename1}*{t0}"
            CONNECTIONS[1].sendall(send_data.encode(FORMAT))

        else:
            #upload from ADDRESSES[0]
            send_data = f"REQUESTM2*{filename2}*{filename1}*{t0}"
            CONNECTIONS[0].sendall(send_data.encode(FORMAT))
    
#Download function multiople strategy 3
def downloadm3(conn:socket.socket, addr, recieved):
    filename1 = recieved[1]
    filename2 = recieved[2]
    t0 = recieved[3]
    files = os.listdir(SERVER_PATH)

    if filename1 not in DOWNLOADS:
         DOWNLOADS[filename1] = 0

    if  filename2 not in DOWNLOADS:
        DOWNLOADS[filename2] = 0

    if filename1 not in files:        
        DELETEME.append(filename1)
        global numDeletes
        numDeletes += 1
        
        if(addr == ADDRESSES[0]):
            #upload from ADDRESSES[1]
            send_data = f"REQUESTM3*{filename1}*{filename2}*{t0}"
            CONNECTIONS[1].sendall(send_data.encode(FORMAT))
            

        else:
            #upload from ADDRESSES[0]
            send_data = f"REQUESTM3*{filename1}*{filename2}*{t0}"
            CONNECTIONS[0].sendall(send_data.encode(FORMAT))
            

    if filename2 not in files:
        DELETEME.append(filename2) 
        numDeletes += 1
        if(addr == ADDRESSES[0]):
            #upload from ADDRESSES[1]
            send_data = f"REQUESTM3*{filename2}*{filename1}*{t0}"
            CONNECTIONS[1].sendall(send_data.encode(FORMAT))

        else:
            #upload from ADDRESSES[0]
            send_data = f"REQUESTM3*{filename2}*{filename1}*{t0}"
            CONNECTIONS[0].sendall(send_data.encode(FORMAT))
    

#Ready, start writing
def ready(conn: socket.socket, recieved):
    filename = recieved[1]
    fileSize = recieved[2]
    fileSize = int(fileSize)
    print("got ready")
    with open(f"{SERVER_PATH}\{filename}", "rb") as f:
        for l in f: 
            conn.sendall(l)
        f.close()

#Upload function
def upload(conn: socket.socket, recieved):
    name = recieved[1]
    filepath = os.path.join(SERVER_PATH, name)
    msg = f"READY*{name}"
    conn.sendall(msg.encode(FORMAT))
    fileSize = conn.recv(SIZE).decode(FORMAT)
    fileSize = int(fileSize)
    data = bytearray()
    with open(filepath,"wb") as f:
        while len(data) != fileSize:
            l = conn.recv(SIZE)
            f.write(l)
            data.extend(l)
            print(f"Recieved {len(data)} bytes of {fileSize} bytes")
    t0 = recieved[2]
    fileSize = str(fileSize)
    send_data = f"DONE*File uploaded successfully*{t0}*{fileSize}"
    conn.sendall(send_data.encode(FORMAT))

#List dir function
def dir(conn: socket.socket):
    files = os.listdir(SERVER_PATH)
    for item in files:
        if item not in DOWNLOADS:
            DOWNLOADS[item] = 0
    msg = "DONE*"
    #If no files in DIR mark msg to empty
    if len(files) == 0:
        msg += "The server directory is empty"
    #Else, there are files, 
    else:
        for item in os.scandir(SERVER_PATH):
            if item.name not in DOWNLOADS:
                DOWNLOADS[item.name] = 0
            modified = datetime.datetime.fromtimestamp(item.stat().st_atime, tz=datetime.timezone.utc)
            msg += f"NAME: {item.name}  SIZE: {item.stat().st_size} BYTES   UPLOAD DATE AND TIME: {modified} UTC   Downloads: {DOWNLOADS[item.name]}\n"
        conn.sendall(msg.encode(FORMAT))

#Request function
def request(conn: socket.socket, addr, recieved):
#Recieve file
    name = recieved[1]
    fileSize = recieved[2]
    t0 = recieved[3]
    filepath = os.path.join(SERVER_PATH, name)
    msg = f"READYD*{name}*{fileSize}"
    conn.sendall(msg.encode(FORMAT))

    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = conn.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")

    if name not in DOWNLOADS:
        DOWNLOADS[name] = 0

    if(addr == ADDRESSES[0]):
        #if recieved from client 0, send to client 1
        send_data = f"DOWNLOADX*{name}*{fileSize}*{t0}"
        CONNECTIONS[1].sendall(send_data.encode(FORMAT))
    else:
        #otherwise, we recieved the file from client 1, and client 0 needs it
        send_data = f"DOWNLOADX*{name}*{fileSize}*{t0}"
        #msg += "File downloaded successfully."
        DOWNLOADS[name] = 0 
        CONNECTIONS[0].sendall(send_data.encode(FORMAT))

def requestm1(conn:socket.socket, addr, recieved):
    name = recieved[1] #good name
    fileSize = recieved[2]
    name2 = recieved[3] #bad name
    t0 = recieved[4]
    filepath = os.path.join(SERVER_PATH, name)
    msg = f"READYD*{name}*{fileSize}"
    conn.sendall(msg.encode(FORMAT))

    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = conn.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")

    fileSize2 = int(os.path.getsize(f"{SERVER_PATH}\{name2}"))
    totalFileSize = fileSize + fileSize2
    print(totalFileSize)
    send_data = f"DOWNLOAD1*{name}*{fileSize}*{name2}*{t0}*{totalFileSize}"
    
    if(addr == ADDRESSES[0]):
        CONNECTIONS[1].sendall(send_data.encode(FORMAT))
    else:
        CONNECTIONS[0].sendall(send_data.encode(FORMAT))

#Request multiple part 2
def requestm2(conn: socket.socket, addr, recieved):


    name = recieved[1]
    fileSize = recieved[2]
    name2 = recieved[3]
    t0 = recieved[4]
    filepath = os.path.join(SERVER_PATH, name)
    msg = f"READYD*{name}*{fileSize}"
    conn.sendall(msg.encode(FORMAT))

    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = conn.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")

    send_data = f"FINISHM2*{name}*{name2}*{fileSize}*{t0}"
    if(addr == ADDRESSES[0]):
        CONNECTIONS[1].sendall(send_data.encode(FORMAT))
    else:
        CONNECTIONS[0].sendall(send_data.encode(FORMAT))

#Request multiple part 3
def requestm3(conn: socket.socket, addr, recieved):
    name = recieved[1]
    fileSize = recieved[2]
    name2 = recieved[3]
    t0 = recieved[4]
    filepath = os.path.join(SERVER_PATH, name)
    msg = f"READYD*{name}*{fileSize}"
    conn.sendall(msg.encode(FORMAT))

    fileSize = int(fileSize)
    dataRecieved = bytearray()
    with open(filepath, "wb") as f:
        while len(dataRecieved) != fileSize:
            l = conn.recv(SIZE)
            f.write(l)
            dataRecieved.extend(l)
            print(f"Recieved {len(dataRecieved)} bytes of {fileSize} bytes")

    send_data = f"FINISHM3*{name}*{name2}*{fileSize}*{t0}"

    if(addr == ADDRESSES[0]):
        CONNECTIONS[1].sendall(send_data.encode(FORMAT))
    else:
        CONNECTIONS[0].sendall(send_data.encode(FORMAT))

#Finish multiple part 2
def finishm2(conn: socket.socket, recieved):
    filename1,filename2 = recieved[1], recieved[2]
    t0 = recieved[3]
    if pathlib.Path(filename1).suffix == '.mp3' or pathlib.Path(filename1).suffix == '.txt':
        with open(f"{SERVER_PATH}\{filename1}", "rb") as f:
            data = f.read()

        with open(f"{SERVER_PATH}\{filename2}", "rb") as f:
            data2 = f.read()

        data3 = data + data2
        DOWNLOADS[filename1] += 1
        DOWNLOADS[filename2] += 1
        filename1 = filename1.split(".")
        filename3 = filename1[0] +"+"+ filename2

        with open(f"{SERVER_PATH}\{filename3}", "wb") as f:
            f.write(data3)
    else:
        data1 = f"file '{filename1}'\n"
        data2 = f"file '{filename2}'"
        data3 = data1 + data2
        
        with open(f"{SERVER_PATH}\mylist.txt",'w') as f:
            f.write(data3)

        filename1 = filename1.split(".")
        filename3 = filename1[0] +"+"+ filename2
        os.system(f"ffmpeg -f concat -safe 0 -i C:/Users/jimne/VisualStudioCode/CS371Project/Multithreaded-File-Transfer-using-TCP-Socket-in-Python/server_data/mylist.txt -c copy {SERVER_PATH}\\{filename3}")
        os.system(f"del {SERVER_PATH}\mylist.txt") 

    if filename3 not in DOWNLOADS:
        DOWNLOADS[filename3] = 0
    fileSize = str(os.path.getsize(f"{SERVER_PATH}\{filename3}"))
    send_data = f"DOWNLOADX*{filename3}*{fileSize}*{t0}"
    conn.sendall(send_data.encode(FORMAT))
    global numDeletes
    os.system(f"del {SERVER_PATH}\{DELETEME[numDeletes]}")

#Finism multiple part 3
def finishm3(conn: socket.socket, recieved):
    filename1, filename2 = recieved[1], recieved[2]
    t0 = recieved[3]
    fileSize1 = str(os.path.getsize(f"{SERVER_PATH}\{filename1}"))
    fileSize2 = str(os.path.getsize(f"{SERVER_PATH}\{filename2}"))
    global totalFileSize 
    totalFileSize = int(fileSize1) + int(fileSize2)
    global numDeletes
    if DELETEME[numDeletes] == filename1:
        send_data = f"DOWNLOAD3*{filename1}*{fileSize1}*{filename2}*{fileSize2}*{t0}"
        conn.sendall(send_data.encode(FORMAT))
    else:
        send_data = f"DOWNLOAD3*{filename2}*{fileSize2}*{filename1}*{fileSize1}*{t0}"
        conn.sendall(send_data.encode(FORMAT))
    
#Delete function
def delete(conn: socket.socket, recieved):
    files = os.listdir(SERVER_PATH)
    msg = "DONE*"
    filename = recieved[1]

    if len(files) == 0:
        msg += "The server directory is empty"
        #Windows del command
    else:
        if filename in files:
            os.system(f"del {SERVER_PATH}\{filename}")
            msg += "File deleted successfully."
        else:
            msg += "File not found."

    conn.sendall(msg.encode(FORMAT))

#Acknowledge delete after borrowing
def ackd(conn: socket.socket, recieved):
    files = os.listdir(SERVER_PATH)
    msg = "DONE*"
    filename = recieved[1]
    t0 = recieved[2]
    fileSize = recieved[3]
    if len(files) == 0:
        msg += "The server directory is empty"
        #Delete after borrowing
    else:
        if filename in files:
            os.system(f"del {SERVER_PATH}\{filename}")
            msg += f"File successfully downloaded, server cleaned.*{t0}*{fileSize}"
            DOWNLOADS[filename] += 1
        else:
            msg += "File not found."
                
    conn.sendall(msg.encode(FORMAT)) 

def ackd1(conn:socket.socket, recieved):
    files = os.listdir(SERVER_PATH)
    msg = "DOWNLOADM1*"
    filename = recieved[1]
    t0 = recieved[2]
    fileSize = recieved[3]
    newName = recieved[4]
    global totalFileSize
    global m1
    totalFileSize = totalFileSize + int(fileSize)
    if len(files) == 0:
        msg += "The server directory is empty"
        #Delete after borrowing
    else:
        if filename in files:
            os.system(f"del {SERVER_PATH}\{filename}")
            msg += f"{filename}*{newName}*{t0}"
            DOWNLOADS[filename] += 1
        else:
            msg += "File not found."
                
    conn.sendall(msg.encode(FORMAT)) 
    m1 = True
    FILENAMES.append(filename)

#Acknowledge and delete part 3
def ackd3(conn: socket.socket, recieved):
    fileName2 = recieved[2]
    fileSize2 = recieved[3]
    t0 = recieved[4]
    global totalFileSize
    os.system(f"del {SERVER_PATH}\{DELETEME[numDeletes]}")
    send_data = f"DOWNLOAD*{fileName2}*{fileSize2}*{t0}*{totalFileSize}"
    conn.sendall(send_data.encode(FORMAT))
    
#Acknowledge
def ack(conn: socket.socket, recieved):
    files = os.listdir(SERVER_PATH)
    filename = recieved[1]
    t0 = recieved[2]
    fileSize = recieved[3]
    msg = f"DONE*File downloaded successfully*{t0}*{fileSize}"
    DOWNLOADS[filename] += 1
    conn.sendall(msg.encode(FORMAT))
    global totalFileSize
    global m1
    totalFileSize = 0

#Error
def err(recieved, addr):
    
    msg = "DONE*"+recieved[1]
    if addr == ADDRESSES[0]:
        #if recieved error from first address, send message to second
        CONNECTIONS[1].sendall(msg.encode(FORMAT))
    else:
        #else, recieved error from second client, so send message to first
        CONNECTIONS[0].sendall(msg.encode(FORMAT))

#Listen for commands to run functions
def handle_client(conn: socket.socket, addr):
    ADDRESSES.append(addr)
    CONNECTIONS.append(conn)
    print(f"[ CONNECTION ] {addr} connected.")
    conn.send("DONE*DIR - List files in server\nUPLOAD filename - upload to path\nDELETE filename - remove file from server\nDOWNLOAD filename - Download file from server\nDOWNLOADM1 filename filename - download one filename at a time\nDOWNLOADM2 filename filename - retrieve one file from client 2 concatenate with other file in server\nDOWNLOADM3 filename filename - retrieve file from client send one at a time\nLOGOUT".encode(FORMAT))

    while True:
        recieved = conn.recv(SIZE).decode(FORMAT)
        recieved = recieved.split("*")
        cmd = recieved[0]

        #List files in DIR
        if cmd == "DIR":
            dir(conn)

        elif cmd == "UPLOAD":
            upload(conn, recieved)

        elif cmd == "DOWNLOAD":
            download(conn, addr, recieved[1], recieved[2])

        elif cmd == "DOWNLOADM1":
            downloadm1(conn, addr, recieved)

        elif cmd == "DOWNLOADM2":
            downloadm2(conn, addr, recieved)

        elif cmd == "DOWNLOADM3":
            downloadm3(conn, addr, recieved)

        elif cmd == "REQUEST":
            request(conn, addr, recieved)

        elif cmd == "REQUESTM1":
            requestm1(conn,addr,recieved)

        elif cmd == "REQUESTM2":
            requestm2(conn, addr, recieved)

        elif cmd == "REQUESTM3":
            requestm3(conn, addr, recieved)

        elif cmd == "DELETE":
            delete(conn, recieved)

        #Acknowledge then delete
        elif cmd == "ACKD":
            ackd(conn, recieved)
        
        elif cmd == "ACKD1":
            ackd1(conn,recieved)

        #Acknowledge then delete multiple part 3
        elif cmd == "ACKD3":
            ackd3(conn, recieved)

        elif cmd == "ACK":
            ack(conn, recieved)

        elif cmd == "ERR":
            err(recieved, addr)

        elif cmd == "READY":
            ready(conn, recieved)

        elif cmd == "FINISHM2":
            finishm2(conn, recieved)
          
        elif cmd == "FINISHM3":
            finishm3(conn, recieved)

        elif cmd == "LOGOUT":
            msg = "DISCONNECTED*Disconnected from server."
            conn.sendall(msg.encode(FORMAT))
            break

        else:
            msg = "DONE*Invalid Input"
            conn.sendall(msg.encode(FORMAT))

    print(f"[DISCONNECT] {addr} disconnected")
    conn.close()

def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(2)
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
