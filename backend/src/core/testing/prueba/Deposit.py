import json
import requests

server_public_key = "GC3EX2UFTJVITCOXBLIFNJMD55SB2DWABEIV2URUX7ZSYCVP76ALZSRY"
server_url = "https://stellar-tesnet.alfred-pay.com/"

def get_token(url1, account1):
    params = (("account", account1),)
    request = requests.get(f"{url1}auth2", params=params)
    print(request)
    data = {"transaction": json.loads(request.text)["transaction"]}
    request = requests.post(f"{url1}auth2", data=data)
    print(request)
    token = json.loads(request.text)["token"]
    return token
server_token=get_token(server_url, server_public_key)

def get_transaction_interactive(token, account, asset_code, asset_issuer, url, operation):
    headers_dict = {"Authorization" : "Bearer "+token}
    data = {"account": account, "asset_code": asset_code, "asset_issuer": asset_issuer}
    request = requests.post(f"{url}sep24/transactions/{operation}/interactive",
        headers=headers_dict, data=data)
    print(request)
    r1 = json.loads(request.text)["url"]
    return r1

deposito1 = get_transaction_interactive(
    token=server_token, account=server_public_key,
    asset_code="TEST", asset_issuer=None, url=server_url, operation="deposit",)
print(deposito1)
"""
deposito2 = deposito1.split("webapp")[1]
url_nueva = f"https://stellar-tesnet.alfred-pay.com/sep24/transactions/deposit/webapp{deposito2}"
print(url_nueva)
print(requests.get(url_nueva))
"""
