#!/bin/bash

# Script to start Ganache, compile and deploy CertificateRegistry, update .env,
# and optionally run Streamlit app.

# Configuration
PROJECT_DIR="$HOME/cert-verification-dapp/Certificate-Verification-Using-Block-Chain-Technology"
ENV_FILE="$PROJECT_DIR/.env"
GANACHE_PORT=8545
LOG_FILE="$PROJECT_DIR/deployment.log"
VENV_DIR="$PROJECT_DIR/venv"

# Ensure required tools are installed
command -v ganache >/dev/null 2>&1 || { echo "Error: ganache is not installed. Install with 'npm install -g ganache'."; exit 1; }
command -v truffle >/dev/null 2>&1 || { echo "Error: truffle is not installed. Install with 'npm install -g truffle'."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "Error: jq is not installed. Install with 'sudo apt install jq'."; exit 1; }

# Change to project directory
cd "$PROJECT_DIR" || { echo "Error: Could not change to project directory $PROJECT_DIR."; exit 1; }

# Start Ganache in the background and log output
echo "Starting Ganache on port $GANACHE_PORT..."
ganache --port $GANACHE_PORT > "$LOG_FILE" 2>&1 &
GANACHE_PID=$!
sleep 5  # Wait for Ganache to start

# Check if Ganache is running
if ! ps -p $GANACHE_PID > /dev/null; then
    echo "Error: Ganache failed to start. Check $LOG_FILE for details."
    exit 1
fi

# Compile the contract
echo "Compiling contract..."
rm -rf build  # Force recompilation
truffle compile >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Contract compilation failed. Check $LOG_FILE."
    kill $GANACHE_PID
    exit 1
fi

# Deploy the contract
echo "Deploying contract..."
truffle migrate --network development --reset >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Contract deployment failed. Check $LOG_FILE."
    kill $GANACHE_PID
    exit 1
fi

# Extract the contract address from build/contracts/CertificateRegistry.json
CONTRACT_JSON="$PROJECT_DIR/build/contracts/CertificateRegistry.json"
if [ ! -f "$CONTRACT_JSON" ]; then
    echo "Error: $CONTRACT_JSON not found."
    kill $GANACHE_PID
    exit 1
fi

CONTRACT_ADDRESS=$(jq -r '.networks | to_entries | .[] | select(.value.address != null) | .value.address' "$CONTRACT_JSON")
if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "Error: Could not extract contract address from $CONTRACT_JSON."
    kill $GANACHE_PID
    exit 1
fi

echo "Contract deployed at address: $CONTRACT_ADDRESS"

# Update .env file
echo "Updating .env file..."
if [ -f "$ENV_FILE" ]; then
    # Remove existing CONTRACT_ADDRESS
    sed -i '/^CONTRACT_ADDRESS=/d' "$ENV_FILE"
fi
# Append new CONTRACT_ADDRESS
echo "CONTRACT_ADDRESS=$CONTRACT_ADDRESS" >> "$ENV_FILE"

# Verify .env update
if grep -q "CONTRACT_ADDRESS=$CONTRACT_ADDRESS" "$ENV_FILE"; then
    echo ".env updated successfully with CONTRACT_ADDRESS=$CONTRACT_ADDRESS"
else
    echo "Error: Failed to update .env file."
    kill $GANACHE_PID
    exit 1
fi

# Optionally activate virtual environment and run Streamlit
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "Running Streamlit app..."
    streamlit run app.py &
    STREAMLIT_PID=$!
    echo "Streamlit running (PID: $STREAMLIT_PID). Open http://localhost:8501"
else
    echo "Warning: Virtual environment not found at $VENV_DIR. Skipping Streamlit."
fi

# Keep Ganache running
echo "Ganache is running (PID: $GANACHE_PID). Press Ctrl+C to stop."
wait $GANACHE_PID