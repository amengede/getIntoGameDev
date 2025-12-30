import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(input("Connect on port: "))
s.connect(("192.168.1.107", port))
this = input("Press any key to exit:")