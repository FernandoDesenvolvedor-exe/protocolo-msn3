# O PROTOCOLO SERA COMPOSTO POR CABEÇALHO COM INFORMAÇÕES DE QUEM ENVIOU
from socket import *
import requests
import json
import threading
import time
import queue


    
# VARIAVEIS GLOBAIS
# Fila para armazenar mensagens recebidas, para exibição na tela
mensagens_recebidas = queue.Queue() 
tuplaDestino = ('localhost',12000)
msn3HeaderParams = ["RS","AUTH","CDS","RDS"]
#ip_publico = requests.get('https://api.ipify.org/').text 


# FUNÇÕES
def getPrivateIp():
    try:
        # Cria um socket de conexão para determinar o IP privado
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Conecta a um servidor externo (Google DNS)
            ip = s.getsockname()[0]    # Obtém o IP da máquina
        return ip
    except Exception as e:
        return f"Erro ao obter IP privado: {e}"

def receber_mensagens():
    # Configura o socket de servidor para receber mensagens
    server_socket = socket.socket(AF_INET, SOCK_STREAM)
    server_socket.bind(tuplaDestino)
    server_socket.listen(1)
    print("Aguardando conexão para receber mensagens...")

    # Aceita a conexão quando o outro usuário estiver pronto
    conn, addr = server_socket.accept()
    print(f"Conectado com {addr}")

    while True:
        mensagem = conn.recv(1024).decode()
        if mensagem.lower() == 'sair':
            print("O outro usuário encerrou a conexão.")
            break
        mensagens_recebidas.put(f"Outro: {mensagem}")  # Adiciona a mensagem recebida na fila

    conn.close()
    server_socket.close()

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
    if request.find("--H") != -1:
        request = request.split("--H")
    elif request.find("--RESP"):
        request = request.split("--RESP")

    resp_h = request[0].strip().split("&")
    resp_b = request[1].strip().split("&")

    requestData = {"header": {}}   

    for data in resp_h:
        key_data = data.split("=")
        requestData["header"][key_data[0]] = key_data[1]

    try:
        for method in msn3HeaderParams:
            if requestData["header"]["RES"] != method:
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
    except KeyError:
        requestData["header"]["RES"] = ""
        requestData["header"]["RESPR"] = ""    

    try:
        requestData["header"]["CNTT"] = resp_h[3]
    except IndexError:
        requestData["header"]["CNTT"] = ""
    
    requestData["body"] = resp_b  

    return requestData

def conversas(userid,limiter):
    msg = "MET=CDS&SND="+ip_privado+"&RES=Conversas("+str(userid)+","+limiter+")--H "
    msg = msg.encode()
    socCli = socket( AF_INET, SOCK_STREAM )
    socCli.connect( tuplaDestino )
    socCli.send(msg)
    resp = socCli.recv(1024)
    socCli.close()

    return parseMsn3Request(resp.decode())

def login(username,password):
    msg = "MET=AUTH&SND="+ip_privado+"&RES=Login("+username+","+password+")--H"
    msg = msg.encode()
    socCli = socket( AF_INET, SOCK_STREAM )
    socCli.connect( tuplaDestino )
    socCli.send(msg)
    resp = socCli.recv(1024)
    socCli.close()
    
    return parseMsn3Request(resp.decode())

ip_privado = getPrivateIp()


# CÓDIGO PRINCIPAL
while True:
    
    print("")
    print("")
    print("-----------------------------")
    print("App de Mensagens")
    print("-----------------------------")
    print("")
    print("")
    print("1 - Login")
    print("2 - Sair")
    print("")

    opcao = int(input("Escolha uma opcao: "))
    match opcao:
        case 1:
            #username = input("Usuario : ")
            #password = input("Senha: ")

            username = "Fernando"
            password = "123"            

            print("Solicitando authenticacao de usuario")            

            loginData = login(username,password)
            
            if loginData["header"]["STATUS"] == "OK":
                if loginData["body"][0] != "NEG" and loginData["body"][0] != "RNF":
                        userid = loginData["body"][0]

                        while True:
                            print("")
                            print("")
                            print("-----------------------------")
                            print("App de Mensagens - "+username)
                            print("-----------------------------")
                            print("")
                            print("")
                            resp = conversas(userid,"USER_STATUS")

                            print(resp["body"])
                            break

                            resp = resp.split("--H")
                            header = resp[0].split("&")
                            body = resp[1]

                            if header[3] == "json":
                                corpo_conversas = json.loads(resp[1])
                                n = 0
                                
                                for chat in corpo_conversas:
                                    user_chat = corpo_conversas.get(str(chat)).get("usuario")
                                    
                                    print(chat +" - "+user_chat)

                                print("new - Nova conversa")
                                print("quit - Sair")
                                print("")
                                opcao = input("Selecione uma opcao: ")

                                if opcao != "new" and opcao != "quit":
                                    chat = corpo_conversas.get(str(opcao)).get("conversa")                                    

                                    while True:
                                        for users in chat:
                                           print(users[0]+": "+users[1]+" "+users[2])

                                        print(" ")                                        
                                        opcao = int(input("""
                                            1 - Nova mensagem
                                            2 - Voltar
                                                  """))
                                        match opcao:
                                            case 1:
                                                new_msg = input("Nova mensagem: ")
                                            case 2:
                                                break
                                            case _:
                                                print("")
                                                print("Opção inexistente!")
                                                print("")
                                    
                                    
                                    
                            else:
                                corpo_conversas = resp[1]
                                
                            break            
                
            else:
                print("Erro ao autenticar usuario")

        case 2:
            break
        case _:
            print("")
            print("Opcao inválida")
            print("")



    
    
        


