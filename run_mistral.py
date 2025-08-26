import subprocess
import requests
import time
import os
import socket

def free_port_8686():
    try:
        output = subprocess.check_output(["lsof", "-i", ":8686"])
        lines = output.decode().strip().split("\n")[1:] 
        for line in lines:
            if "uvicorn" in line or "python" in line:
                pid = line.split()[1]
                print(f"🔪 Killing process {pid} using port 8686")
                subprocess.run(["kill", "-9", pid])
    except subprocess.CalledProcessError:
        print("OK - Port 8686 is already free.")

def kill_existing_processes():
    print("Cleaning up old processes...")
    os.system("pkill -f 'ollama serve'")
    os.system("pkill -f 'uvicorn main:app'")
    print("OK - done, cleaned up")

def kill_ollama_connections():
    try:
        subprocess.run("lsof -i :11434 | awk 'NR>1 {print $2}' | xargs kill -9", shell=True)
    except Exception as e:
        print(f"ERROR - killing of Ollama processes has failed: {e}")

def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def ollama_running():
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except:
        return False


kill_existing_processes()
kill_ollama_connections()
time.sleep(1)

if not ollama_running():
    print("TASK - Starting Ollama...")
    subprocess.Popen(["ollama", "serve"])
    time.sleep(2)
else:
    print("OK - ollama is running")


timeout = 10
while timeout > 0 and not ollama_running():
    print(f"Waiting for Ollama... ({timeout}s left)")
    time.sleep(1)
    timeout -= 1

if not ollama_running():
    print("ERROR - Ollama is not running. Please open it manually.")
    exit()

free_port_8686()
print("TASK - Starting FastAPI (uvicorn)...")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.Popen(["uvicorn", "main:app", "--port", "8686"])

print("TASK - Starting Streamlit app...")
subprocess.Popen(["streamlit", "run", "frontend.py"])
time.sleep(3)