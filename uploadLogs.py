import time
from web3 import Web3, HTTPProvider
import json
contract_address = "0x10679EAdfE8A3E320541bE772C24A9Ca4debe394"
wallet_private_key = "A126F58A7C4F0605F9FD5EA31DB60B171130B8D4011DA19F86C749CE32D7AD28"
wallet_address = "0x7F7aBe8574f4736cA7310685302DE05b4c2a6698"

w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/834ab6c7f8d34709b6844218289e6336"))

with open("./contract_abi.abi") as f:
    contract_abi = json.load(f)

w3.eth.enable_unaudited_features()

contract = w3.eth.contract(address = contract_address, abi = contract_abi)

def getN():
    return contract.functions.getN().call()

def getWN():
    return contract.functions.getWN().call()

def sendLog(hashedLog):
    while True:
        try:
                nonce = w3.eth.getTransactionCount(wallet_address)
                txn_dict = contract.functions.sendLog(hashedLog).buildTransaction({
                    'chainId': 3,
                    'gas': 140000,
                    'gasPrice': w3.toWei('40', 'gwei'),
                    'nonce': nonce,
                })
                 
                signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)
                result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                tx_rct =  w3.eth.getTransactionReceipt(result)
                break
        except:
                time.sleep(10)
#                nonce += 1
                continue
    count = 0
    while tx_rct is None and (count < 30):
        time.sleep(10)
        tx_rct = w3.eth.getTransactionReceipt(result)
    if tx_rct is None:
        return {'status': 'failed', 'error': 'timeout'}
    return {'status': 'success'}

def getLogs(index):
    return contract.functions.getLogs(index).call()

def init():
    nonce = w3.eth.getTransactionCount(wallet_address)
    txn_dict = contract.functions.init().buildTransaction({
        'chainId': 3,
        'gas': 140000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })
    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)
    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_rct =  w3.eth.getTransactionReceipt(result)
    count = 0
    while tx_rct is None and (count < 30):
        time.sleep(10)
        tx_rct = w3.eth.getTransactionReceipt(result)
    if tx_rct is None:
        return {'status': 'failed', 'error': 'timeout'}
    return {'status': 'success'}

def warning(message):
    t_wallet_address = "0x914c3Ee916c6e5d10450Ac8188B9F182995A3165"
    t_wallet_private_key = "3B330F56E6A529F7D64931CB70856193DB5FE723CD27F8D00BDEF6851BBF6243"
#    while True:
    
    nonce = w3.eth.getTransactionCount(t_wallet_address,'pending')
    txn_dict = contract.functions.warning(message).buildTransaction({
        'chainId': 3,
        'gas': w3.toHex(3000000),
        'gasPrice': w3.toHex(w3.toWei('40', 'gwei')),
        'nonce': nonce,
    })
    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=t_wallet_private_key)
    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
#            break
#            time.sleep(2)
#            continue

    tx_rct =  w3.eth.getTransactionReceipt(result)
    count = 0
    while tx_rct is None and (count < 30):
        time.sleep(10)
        tx_rct = w3.eth.getTransactionReceipt(result)
    if tx_rct is None:
        return {'status': 'failed', 'error': 'timeout'}
    print("")
    print("log upload succeed.")
    print("2>", end="")
    return {'status': 'success'}

def getWarnings(index):
    return contract.functions.getWarning(index).call()



