# O PROTOCOLO SERA COMPOSTO POR CABEÇALHO COM INFORMAÇÕES DE QUEM ENVIOU
from socket import *
from datetime import datetime
#import requests
import json
import threading
import time
import queue


    
# VARIAVEIS GLOBAIS
# Fila para armazenar mensagens recebidas, para exibição na tela
mensagens_recebidas = queue.Queue() 
tuplaDestino = ('localhost',12000)
msn3HeaderParams = ["AUTH","CDS","RDS"]
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

def enviaRequisicao(msg):
    msg = msg.encode()
    socCli = socket( AF_INET, SOCK_STREAM )
    socCli.connect( tuplaDestino )
    socCli.send(msg)
    resp = socCli.recv(1024)
    socCli.close()

    return parseMsn3Request(resp.decode())

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
    
    requestData["body"] = resp_b  

    return requestData

def validaResposta(resposta):    
    if resposta["header"]["STATUS"] == "ERR":
        raise ConnectionError(resposta["body"])

    if resposta["header"].get("CNTT") != None and resposta["header"].get("CNTT") == "json":
        resposta["body"] = json.loads(resposta["body"][0])
        
    return resposta

def contatos(user_id):
    msg = "MET=CDS&SND="+ip_privado+"&RES=Contatos("+str(user_id)+")--H "
    return validaResposta(enviaRequisicao(msg))

def conversas(user_id,contact_id):
    msg = "MET=CDS&SND="+ip_privado+"&RES=Conversas("+str(user_id)+","+contact_id+")--H "
    return validaResposta(enviaRequisicao(msg))

def login(username,password):
    msg = "MET=AUTH&SND="+ip_privado+"&RES=Login("+username+","+password+")--H"
    return validaResposta(enviaRequisicao(msg))

def novaMensagem(user_id,contact_id,msg):
    datahora = datetime.now()
    datahora = datahora.strftime("%Y:%m:%d %H:%M:%S")
    msg = {
        "sender_id": user_id,
        "reciver_id":contact_id,
        "message":msg,
        "datetime":datahora
    }

    msg = "MET=REG&SND="+ip_privado+"&RES=NovaMensagem()&CNTT=json--H "+json.dumps(msg)
    return validaResposta(enviaRequisicao(msg))

def alignCenter():
    return "                                        "

ip_privado = getPrivateIp()


# CÓDIGO PRINCIPAL
while True:    
    print("")
    print("")
    print(f"{alignCenter()}-----------------------------")
    print(f"{alignCenter()}App de Mensagens")
    print(f"{alignCenter()}-----------------------------")
    print("")
    print("")
    print(f"{alignCenter()}1 - Login")
    print(f"{alignCenter()}2 - Sair")
    print("")

    opcao = int(input(f"{alignCenter()}Escolha uma opcao: "))
    match opcao:
        case 1:
            #username = input("Usuario : ")
            #password = input("Senha: ")

            username = "Fernando"
            password = "123"            

            print(f"{alignCenter()}Solicitando authenticacao de usuario")  

            try:
                loginData = login(username,password)
            
                if loginData["body"][0] != "NEG" and loginData["body"][0] != "RNF":                     
                    print("") 
                    print(f"{alignCenter()}Usuario Autorizado")      
                    print("")   

                    user_id = loginData["body"][0]
                    contatos_salvos = contatos(user_id)

                    while True:
                        print(f"""
                                        -----------------------------
                                        App de Mensagens - {username}
                                        -----------------------------
                                        
                                        talk - conversar
                                        new - Novo contato
                                        quit - Sair"
                                                """)
                        opcao = input(f"{alignCenter()}Selecione uma opcao: ")

                        match opcao:
                            case "new":
                                print("algo")
                            case "quit":
                                break
                            case "talk"|"Talk"|"TALK":
                                print("")
                                print("")                                
                                contato = []
                                n = 0                                
                                for chat_index in contatos_salvos["body"]:
                                    contato.append(contatos_salvos["body"].get(chat_index))

                                    print(f"{alignCenter()}{contato[int(chat_index)].get("id")}",end=" ")
                                    print(" - "  + contato[int(chat_index)].get("name"),end=" ")
                                    print(" "+contato[int(chat_index)].get("status"))

                                print(f"{alignCenter()}quit - Voltar")
                                opcao = input(f"{alignCenter()}Conversar com: ")

                                match opcao:
                                    case "quit":
                                        break
                                    case _:
                                        while True:
                                            chat = conversas(user_id,opcao)["body"]
                                            contact_id = opcao
                                            contact_name = chat.get("messages_sent").get("enderecado")
                                        
                                            chat2 = chat.get("messages_received")
                                            chat = chat.get("messages_sent")

                                            chat2.pop("enderecado")
                                            chat.pop("enderecado")
                                            
                                            for index in chat2.get("conversa"):
                                                chat2.get("conversa").get(index).append(contact_name)

                                            for index in chat.get("conversa"):
                                                chat.get("conversa").get(index).append(username)

                                            chat.get("conversa").update(chat2.get("conversa"))
                                            del chat2
                                            chat = chat["conversa"]

                                            print(len(chat))
                                            chat = dict(sorted(chat.items()))

                                            print(f"{alignCenter()}---------------------------------")
                                            print(f"{alignCenter()}Conversa com {contact_name} código({contact_id})")
                                            print(f"{alignCenter()}---------------------------------")       

                                            for index in chat:
                                                print(f"""{alignCenter()}{chat[index][2]}: {chat[index][0]} -- {chat[index][1]}""")

                                            print("")
                                            print(f"{alignCenter()}newm - Nova mensagem")
                                            print(f"{alignCenter()}quit - voltar")
                                            option = input(f"{alignCenter()}Opção: ")
                                            
                                            match option:
                                                case "newm":
                                                    nova_mensagem = input(f"{alignCenter()}Mensagem: ")
                                                    novaMensagem(user_id,contact_id,nova_mensagem)
                                                case "quit":
                                                    break

                            case _:
                                print("TODO")
                else:
                    print("Acesso negado")
            except ConnectionError:
                print("Erro ao tentar se cominicar com servidor")

        case 2:
            break
        case _:
            print("")
            print("Opcao inválida")
            print("")



    
    
        



