This project was made by Ethan Gamble and Jim Nikolic.

After running both clients, the list of usable server commands will show up. Those commands are:

DIR - list contents of server directory along with other properties.

UPLOAD <filename> - Uploads specified filename to the server. If file not in client database, returns an error.

DOWNLOAD <filename> - Downloads specified filename from server to client. If file is on server, file is downloaded onto client and does nothing else.
If file was not on server, reaches out to the other client to retrieve it. If the other client has the file, it is sent to server, then to other client,
and deletes it from server. If file not in server or other client database, returns an error.

DOWNLOADM1 <filename1> <filename2> - downloads multiple files, one file at a time.

DOWNLOADM2 <filename1> <filename2> - downloads multiple files by concatenating them together into one file.

DOWNLOADM3 <filename1> <filename2> - downloads multiple files by retrieving both first, then sending them back to back.

DELETE <filename> - Deletes specified filename from the server. If not on server, returns an error.

LOGOUT- disconnect from server

In each case above, filename must include type(.txt,.mp3,.mp4)

To connect to the server, each client will have to input an IP address and a port number to connect to after running the program.