import subprocess
import time
import os
import platform
import re
import sys
import requests

# Windows-specific check
def check_and_install_pywin32():
    try:
        import win32api
        import win32con
        print("✅ pywin32 is already installed.")
    except ImportError:
        print("❌ pywin32 is not installed.")
        install = input("Do you want to install pywin32? (y/n): ").strip().lower()
        if install == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        else:
            print("⚠️ Cannot proceed without pywin32 on Windows.")
            sys.exit(1)

if platform.system() == "Windows":
    import win32api
    import win32con

# Constants
PROJECT_DIR = os.getcwd()
OUTPUT_FILE = "migrate_output.txt"
ENV_FILE = ".env"
GANACHE_PORT = 8545

# Process handles
ganache_process = None
streamlit_process = None

def open_ganache_process():
    global ganache_process
    print("🚀 Launching Ganache...")
    if platform.system() == "Windows":
        ganache_process = subprocess.Popen(
            ['ganache', '--port', str(GANACHE_PORT)],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
    else:
        ganache_process = subprocess.Popen(
            ['ganache', '--port', str(GANACHE_PORT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def wait_for_ganache(timeout=60):
    print("⏳ Waiting for Ganache to be ready on port 8545...")
    start_time = time.time()
    while True:
        try:
            response = requests.post("http://127.0.0.1:8545", json={
                "jsonrpc":"2.0", "method":"web3_clientVersion", "params":[], "id":1
            }, timeout=2)
            if response.status_code == 200:
                print("🟢 Ganache is up and responding.")
                break
        except Exception:
            pass
        if time.time() - start_time > timeout:
            print("❌ Ganache did not start within time limit.")
            terminate_processes()
            sys.exit(1)
        time.sleep(1)

def run_truffle_compile():
    print("🛠️ Compiling contracts...")
    compile_process = subprocess.run(
        "truffle compile", shell=True, cwd=PROJECT_DIR
    )
    if compile_process.returncode != 0:
        print("❌ Compile failed.")
        terminate_processes()
        sys.exit(1)

def run_truffle_migrate():
    print("📦 Migrating contracts...")
    with open(OUTPUT_FILE, 'w') as file:
        file.write('')
    migrate_process = subprocess.run(
        "truffle migrate --reset --network development",
        shell=True, cwd=PROJECT_DIR,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    with open(OUTPUT_FILE, "w") as file:
        file.write(migrate_process.stdout.decode())
        file.write(migrate_process.stderr.decode())
    print("✅ Migration complete.")

def extract_contract_address(file_path, contract_name="CertificateRegistry"):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    contract_address = None
    inside_target = False
    for line in lines:
        if f"Deploying '{contract_name}'" in line:
            inside_target = True
        elif inside_target and "> contract address:" in line:
            match = re.search(r'0x[a-fA-F0-9]{40}', line)
            if match:
                contract_address = match.group(0)
                break
    return contract_address

def update_env_file(address, env_path=".env"):
    updated_lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r") as file:
            for line in file:
                if line.startswith("CONTRACT_ADDRESS="):
                    updated_lines.append(f"CONTRACT_ADDRESS={address}\n")
                    found = True
                else:
                    updated_lines.append(line)
    if not found:
        updated_lines.append(f"CONTRACT_ADDRESS={address}\n")
    with open(env_path, "w") as file:
        file.writelines(updated_lines)
    print(f"📄 .env updated with contract address: {address}")

def run_streamlit():
    global streamlit_process
    print("🚀 Launching Streamlit app...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=PROJECT_DIR
    )
    try:
        streamlit_process.wait()
    except KeyboardInterrupt:
        pass

def terminate_processes():
    print("🛑 Cleaning up processes...")
    if streamlit_process:
        try:
            streamlit_process.terminate()
            streamlit_process.wait(timeout=5)
            print("✅ Streamlit terminated.")
        except Exception as e:
            print(f"❌ Error terminating Streamlit: {e}")
    if ganache_process:
        try:
            if platform.system() == "Windows":
                print("⚠️ Sending CTRL_BREAK_EVENT to Ganache...")
                win32api.GenerateConsoleCtrlEvent(win32con.CTRL_BREAK_EVENT, ganache_process.pid)
            else:
                ganache_process.terminate()
            ganache_process.wait(timeout=5)
            print("✅ Ganache terminated.")
        except Exception as e:
            print(f"❌ Error terminating Ganache: {e}")

if __name__ == "__main__":
    try:
        print(f"📁 Current directory: {PROJECT_DIR}")
        if not os.path.exists(os.path.join(PROJECT_DIR, "truffle-config.js")):
            raise Exception("❌ Not a Truffle project directory.")
        if platform.system() == "Windows":
            check_and_install_pywin32()
        open_ganache_process()
        wait_for_ganache()
        run_truffle_compile()
        run_truffle_migrate()

        contract_address = extract_contract_address(OUTPUT_FILE)
        if contract_address:
            update_env_file(contract_address)
        else:
            print("❌ Contract address not found in migration logs.")
            terminate_processes()
            sys.exit(1)

        run_streamlit()
    except KeyboardInterrupt:
        print("⛔ Interrupted by user.")
    finally:
        terminate_processes()
        print("✅ All processes cleaned up.")
