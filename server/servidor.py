#
# Servidor
#

from socket import *
import json
import threading
import time
import queue

server_ip = "127.0.0.1"
socketServidor = socket(AF_INET, SOCK_STREAM)
tuplaEscuta = ('',12000)
socketServidor.bind( tuplaEscuta )
socketServidor.listen(True)

msn3HeaderMETS = ["RS","AUTH","CDS","RDS"]

def translateRequestMethod(method):
    match method.upper():
        case "RS":
            return "RESPOSTA DO SERVIDOR"
        case "AUTH":
            return "AUTENTICACAO"
        case "CDS":
            return "CONSULTA DE DADOS DO SERVIDOR"
        case "RDS":
            return "REGISTRAR DADOS NO SERVIDOR"
        case _:
            return "METODO INVALIDO"  

def parseMsn3Request(request):
    request = request.split("--H")
    resp_h = request[0].strip().split("&")
    resp_b = request[1].strip().split("&")

    requestData = {"header": {}}   

    for data in resp_h:
        key_data = data.split("=")
        requestData["header"][key_data[0]] = key_data[1]

    if requestData["header"]["MET"] not in msn3HeaderMETS:
        raise SyntaxError("Metodo nao encontrado")

    if requestData["header"].get("RES") != None: 

        res_param = requestData["header"]["RES"].replace(")","&").replace("(","&").split("&")
        res_param.pop(2)
        res =  res_param[0]
        params = str(res_param[1])

        if params != '':
            params = params.split(",")

        requestData["header"]["RES"] = res
        requestData["header"]["RESPR"] = params  

    try:
        requestData["header"]["CNTT"] = resp_h[3]
    except IndexError:
        requestData["header"]["CNTT"] = ""
    
    requestData["body"] = resp_b  

    return requestData


#               [usuarios]
usuarios = {"Fernando": {"senha":"123","id":0, "IP":"0"},
            "Felipe": {"senha":"123","id":1, "IP":"0"},
            "Guilherme": {"senha":"123","id":2, "IP":"0"},
            "Andressa": {"senha":"123","id":3, "IP":"0"}}

conversas = {
    "0":{
        "1":{
            "usuario":"Felipe",
            "conversa":[
                ["Fernando","Oi mano","2024-12-25 10:33:03"],
                ["Felipe","Aew cara","2024-12-25 10:33:40"],
                ["Fernando","Tudo bem?","2024-12-25 10:33:58"],
                ["Felipe","Tudo certo aqui mano","2024-12-25 10:34:26"]
            ]
        },
        "2":{
            "usuario":"Guilherme",
            "conversa":[
                ["Fernando","Oi mano","2024-12-25 11:30:00"],
                ["Guilherme","Fala","2024-12-25 11:33:40"],
                ["Fernando","Ja buscou a parada la?","2024-12-25 11:35:30"],
                ["Guilherme","Sim","2024-12-25 11:36:20"]
            ]
        },
        "3":{
            "usuario":"Andressa",
            "conversa":[
                ["Fernando","Oi vida","2024-12-25 20:01:03"],
                ["Andressa","Oii","2024-12-25 20:01:15"],
                ["Fernando","Como ta a aula?","2024-12-25 20:02:14"],
                ["Andressa","Entediante","2024-12-25 20:02:23"]
            ]
        }
    },
    "1":{
        "2":{
            "usuario":"Guilherme",
            "conversa":[
                ["Felipe","Oi mano","2024-12-25","11:30:00"],
                ["Guilherme","Fala","2024-12-25","11:33:40"],
                ["Felipe","Ja buscou a parada la?","2024-12-25","11:35:30"],
                ["Guilherme","Sim","2024-12-25","11:36:20"]
            ]
        }
    }
}

while True:
    #
    # Recebe a mensagem
    #
    conexao, endereco = socketServidor.accept()
    mensagem = conexao.recv(1024)
    mensagem = mensagem.decode()

    print(f"Recebido: {mensagem}")

    try:
        data = parseMsn3Request(mensagem)   

        user_ip = data["header"]["SND"]
        method = data["header"]["MET"]
        resource = data["header"]["RES"]

        match method:
            case "AUTH":
                match resource:
                    case "Login":
                        user = data["header"]["RESPR"][0].strip()
                        password = data["header"]["RESPR"][1].strip()
                        
                        if(usuarios.get(user) != None):
                            if(usuarios.get(user).get("senha") == password):
                                usuarios[user]["IP"] = user_ip
                                response = "SND=SERVER&STATUS=OK--RESP "+str(usuarios[user]["id"])
                            else:
                                response = "SND=SERVER&STATUS=OK--RESP NEG"
                        else:
                            response = "SND=SERVER&STATUS=OK--RESP NEG"
                    case _:
                        response = "SND=SERVER&STATUS=ERR--RESP RNF"
            
            case "CDS":
                match resource:
                    case "Conversas":
                        id = data["header"]["RESPR"][0]
                        
                        if conversas.get(id) != None:
                            try:
                                limiter = data["header"]["RESPR"][1].upper()

                                match limiter:
                                    case "USER_STATUS":
                                        users = {}
                                        for chat in conversas.get(id):  
                                            print(chat)                                      
                                            users["usuario"]["name"] = chat["usuario"]
                                            if usuarios.get(chat["usuario"]).get("IP") == "0":
                                                users["usuario"]["status"] = "OFF"
                                            else:
                                                users["usuario"]["status"] = "ON"

                            except IndexError:
                                print("deu ruim pai")
                                

                            response = "SND=SERVER&STATUS=OK&CNTT=json--RESP "+json.dumps(conversas.get(id))
                        else:
                            response = "SND=SERVER&STATUS=OK--RESP  NUF"
                                            
                    case _:
                        response = "SND=SERVER&STATUS=OK--RESP RNF"
                    
            case _:
                response = "SND=SERVER&STATUS=OK--RESP MNS"

    except SyntaxError:
        response = "SND=SERVER&STATUS=ERR--RESP MHP"

        
    print("Respondido :", response)
    print("")
    response = response.encode()
    conexao.send(response)
    conexao.close()
