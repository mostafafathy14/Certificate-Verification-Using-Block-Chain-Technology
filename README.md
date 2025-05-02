# Certificate-Verification-Using-Block-Chain-Technology

## Set Up the Development Environment

### 1\. Install Required Tools

**Node.js and npm**: Required for Truffle and Web3.js.  
Install via `https://nodejs.org/`

**Truffle**: For smart contract development and deployment.  
Run: `npm install -g truffle`

**Ganache**: For a local Ethereum blockchain.  
 Download from https://trufflesuite.com/ganache/ or install via `npm install -g ganache`

**Streamlit**: For the Python-based user interface.  
 Run: `pip install streamlit`

**Web3.py**: For Python blockchain interaction.  
 Run: `pip install web3`

**IPFS (Pinata)**: For decentralized storage.  
 Install Pinata SDK: `pip install pinata-sdk` (requires a Pinata account and API keys from https://pinata.cloud/).

### 2.Build The Project

&nbsp;       1. Run the Ganache Server  
        `ganache --port 8545 ` 

&nbsp;       2. Compile  Truffle  
        `truffle compile`

&nbsp;       3. Deploy the contract  
         `truffle migrate --network development --reset`

&nbsp;       4. Copy the Contract_Address from the 2_deploy_contracts.js field its start with 0x123......

&nbsp;       5. paste it in the .env file

&nbsp;       6.Run the Streamlt  
        `streamlit run app.py`

### 3.Its Done :D
