from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:PORT"))  # replace with your own endpoint
print(web3.isConnected())
