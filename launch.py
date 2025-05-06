import subprocess
import time
import os
import platform
import re
import sys
# Check if pywin32 is installed, if not, try to install it
def check_and_install_pywin32():
    try:
        import win32api
        import win32con
        print("✅ pywin32 is already installed.")
    except ImportError:
        print("❌ pywin32 is not installed.")
        install_pywin32 = input("Do you want to install pywin32? (y/n): ").strip().lower()
        if install_pywin32 == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
                print("✅ pywin32 installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install pywin32: {e}")
                sys.exit(1)
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
    system = platform.system()

    print("🚀 Launching Ganache...")

    if system == "Windows":
        ganache_process = subprocess.Popen(
            ['ganache', '--port', str(GANACHE_PORT)],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
    else:
        ganache_process = subprocess.Popen(
            ['ganache', '--port', str(GANACHE_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    time.sleep(5)
    print(f"🟢 Ganache started with PID {ganache_process.pid}")


def run_truffle_compile():
    print("🛠️ Running Truffle Compile...")
    truffle_cmd = "truffle compile"
    compile_process = subprocess.Popen(
        truffle_cmd, shell=True, cwd=PROJECT_DIR,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = compile_process.communicate()
    print(stdout.decode())
    if stderr:
        print("⚠️ Truffle compile errors:\n", stderr.decode())


def run_truffle_migrate():
    print("🛠️ Running Truffle Migrate...")
    truffle_cmd = "truffle migrate --network development --reset"
    with open(OUTPUT_FILE, 'w') as file:
        file.write('')

    migrate_process = subprocess.Popen(
        truffle_cmd, shell=True, cwd=PROJECT_DIR,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = migrate_process.communicate()

    with open(OUTPUT_FILE, "w") as file:
        file.write(stdout.decode())
        file.write(stderr.decode())

    print("✔️ Truffle migration complete.")


def extract_contract_address(file_path, contract_name="CertificateRegistry"):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    contract_address = None
    inside_target_deploy = False
    for line in lines:
        if f"Deploying '{contract_name}'" in line:
            inside_target_deploy = True
        elif inside_target_deploy and "> contract address:" in line:
            match = re.search(r'> contract address:\s+(0x[a-fA-F0-9]+)', line)
            if match:
                contract_address = match.group(1)
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


def run_streamlit():
    global streamlit_process
    print("🚀 Running Streamlit...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=PROJECT_DIR
    )

    try:
        streamlit_process.communicate()
    except KeyboardInterrupt:
        pass


def terminate_ganache_and_streamlit():
    print("⏹️ Terminating processes...")

    if streamlit_process:
        try:
            streamlit_process.terminate()
            streamlit_process.wait()
            print("✅ Streamlit terminated.")
        except Exception as e:
            print(f"❌ Error terminating Streamlit: {e}")

    if ganache_process:
        try:
            if platform.system() == "Windows":
                print("⚠️ Sending CTRL_BREAK_EVENT to Ganache...")
                win32api.GenerateConsoleCtrlEvent(win32con.CTRL_BREAK_EVENT, ganache_process.pid)
                ganache_process.wait(timeout=5)
                print("✅ Ganache terminated with CTRL_BREAK_EVENT.")
            else:
                ganache_process.terminate()
                ganache_process.wait(timeout=5)
                print("✅ Ganache terminated with SIGTERM.")
        except Exception as e:
            print(f"❌ Error terminating Ganache: {e}")


if __name__ == "__main__":
    try:
        print(f"📁 Checking project directory: {PROJECT_DIR}")
        if not os.path.exists(os.path.join(PROJECT_DIR, "truffle-config.js")):
            raise Exception("❌ Not in correct project directory. 'truffle-config.js' not found.")
        if platform.system() == "Windows":
            check_and_install_pywin32()
        open_ganache_process()
        run_truffle_compile()
        run_truffle_migrate()

        contract_address = extract_contract_address(OUTPUT_FILE)

        if contract_address:
            print(f"✅ Contract address: {contract_address}")
            update_env_file(contract_address)
        else:
            print("❌ Contract address not found in migration output.")

        run_streamlit()

    except KeyboardInterrupt:
        print("\n⛔ KeyboardInterrupt received.")
    finally:
        terminate_ganache_and_streamlit()
        print("✅ All processes cleaned up.")
