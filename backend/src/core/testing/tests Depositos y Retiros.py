import json
import requests

# Server Public Key. #
server_public_key = "GC3EX2UFTJVITCOXBLIFNJMD55SB2DWABEIV2URUX7ZSYCVP76ALZSRY"
server_url = "http://localhost:8003/"
server_token_doc = "server_token.log"

# Client Public Key. #
client_public_key = "GAB5XGSIDA3VU2DUOVIWOJ5SFHZFRTSDNB5G3B5Z5IWXZWXKMVRIMSO4"
client_url = "http://localhost:8004/"
client_token_doc = "client_token.log"

# """
def get_token(url1, account1):
    # Parte 1 Generacion del Token y archivo JSON con la información correspondiente. #
    params = (
        ("account", account1),
        ("home_domain", url1[7:-1]),
        ("client_domain", url1[7:-1])
    )
    request = requests.get(f"{url1}auth", params=params)
    data = {"transaction": json.loads(request.text)["transaction"]}
    request = requests.post(f"{url1}auth", data=data)
    token = json.loads(request.text)["token"]
    return token

with open("registro1.json", 'w', encoding='utf-8') as file:
    server_token = get_token(
        url1=server_url,
        account1=server_public_key,
    )
    reporte = {"Titulo": "Pruebas para obtener un Token, usando la cuenta del servidor!"}
    reporte["account"] = server_public_key
    reporte["Comment1"] = f"Realizamos GET en {server_url} para obtener transaction para esa account."
    reporte["Comment2"] = f"Con esa transaction, se realiza un POST en {server_url} para obtener el Token de la cuenta del servidor!"
    reporte["server token"] = server_token
    json.dump(reporte, file, ensure_ascii=False, indent=4)
    print(f"Salvado el archivo {file.name} con el reporte {reporte}!")

"""
with open("registro1.json") as file1:
    # Parte 1b para evitar repetir la generacion del Token se puede comentar
    # la parte 1 y usar el registro correspondiente.
    # Comentar la parte 1 y descomentar la parte 1b en ese caso. #
    server_token = json.load(file1)["server token"]
"""

def get_transaction_interactive(
    token, account, asset_code, asset_issuer, url, operation
    ):
    # Parte 2 Funcion para transacciones Deposito/Retiros Interactiva. #
    headers_dict = {"Authorization" : "Bearer "+token}
    data = {"account": account,
        "asset_code": asset_code,
        "asset_issuer": asset_issuer
        }
    request = requests.post(
        f"{url}sep24/transactions/{operation}/interactive",
        headers=headers_dict, data=data
        )
    r1 = json.loads(request.text)
    return r1

with open("registro_deposito.json", 'w', encoding='utf-8') as file:
    # Parte 3 Prueba para Deposito. #
    operation = "deposit"
    asset_code = "TEST"
    deposito1 = get_transaction_interactive(
        token=server_token, account=server_public_key,
        asset_code=asset_code, asset_issuer=client_public_key,
        url=server_url, operation=operation,
    )
    reporte = {"Titulo": f"Prueba para realizar un {operation} Interactivo, usando la cuenta del servidor!"}
    reporte["Comment1"] = f"Obtenido el Token de la cuenta del Servidor podemos agregarlo al POST de {server_url}sep24/transactions/{operation}/interactive dentro del headers_dict, adicional enviamos de parametros el get_transaction_interactive_data con los datos de la cuenta y el asset."
    reporte["get_transaction_interactive_headers_dict"]= {"Authorization": "Bearer "+server_token}
    reporte["get_transaction_interactive_data"] = {"account": server_public_key, "asset_code": asset_code}
    reporte["get_transaction_interactive"] = deposito1
    reporte["Comment2"] = f"Obtenido el 1 paso del {operation} Interactivo!"
    json.dump(reporte, file, ensure_ascii=False, indent=4)
    print(f"Salvado el archivo {file.name} con el reporte {reporte}!")
    print(f"\n\nPara continuar la operacion usar la url que se presenta a continuación en el navegador:")
    print(deposito1['url'])

with open("registro_retiro.json", 'w', encoding='utf-8') as file:
    # Parte 3 Prueba para Retiro. #
    operation = "withdraw"
    asset_code = "TEST"
    retiro1 = get_transaction_interactive(
        token=server_token, account=server_public_key,
        asset_code=asset_code, asset_issuer=client_public_key,
        url=server_url, operation=operation,
    )
    reporte = {"Titulo": f"Prueba para realizar un {operation} Interactivo, usando la cuenta del servidor!"}
    reporte["Comment1"] = f"Obtenido el Token de la cuenta del Servidor podemos agregarlo al POST de {server_url}sep24/transactions/{operation}/interactive dentro del headers_dict, adicional enviamos de parametros el get_transaction_interactive_data con los datos de la cuenta y el asset."
    reporte["get_transaction_interactive_headers_dict"]= {"Authorization": "Bearer "+server_token}
    reporte["get_transaction_interactive_data"] = {"account": server_public_key, "asset_code": asset_code}
    reporte["get_transaction_interactive"] = retiro1
    reporte["Comment2"] = f"Obtenido el 1 paso del {operation} Interactivo!"
    json.dump(reporte, file, ensure_ascii=False, indent=4)
    print(f"Salvado el archivo {file.name} con el reporte {reporte}!")
    print(f"\n\nPara continuar la operacion usar la url que se presenta a continuación en el navegador:")
    print(retiro1['url'])
