# O PROTOCOLO SERA COMPOSTO POR CABEÇALHO COM INFORMAÇÕES DE QUEM ENVIOU
from socket import *
from datetime import datetime
#import requests
import json
import threading
import time
import queue
import os
import platform
import subprocess
import sys
    
# VARIAVEIS GLOBAIS
tuplaDestino = ('192.168.1.23',12000)
msn3HeaderParams = ["AUTH","CDS","RDS"]
#ip_publico = requests.get('https://api.ipify.org/').text 

# Fila para armazenar mensagens recebidas, para exibição na tela
mensagens_recebidas = queue.Queue()

# FUNÇÕES
def limpaTela():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def getPrivateIp():
    try:
        # Cria um socket de conexão para determinar o IP privado
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Conecta a um servidor externo (Google DNS)
            ip = s.getsockname()[0]    # Obtém o IP da máquina
        return ip
    except Exception as e:
        return f"Erro ao obter IP privado: {e}"

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

def carregaMensagem(user_id,contact_id):
    msg = "MET=CDS&SND="+ip_privado+"&RES=Conversas("+str(user_id)+","+contact_id+")--H "

def login(username,password):
    msg = "MET=AUTH&SND="+ip_privado+"&RES=Login("+username+","+password+")--H"
    return validaResposta(enviaRequisicao(msg))

def enviarMensagem(user_id,contact_id):
    msg = input(f"{alignCenter()}Mensagem: ")
    datahora = datetime.now()
    datahora = datahora.strftime("%Y:%m:%d %H:%M:%S")
    msg = {
        "sender_id": user_id,
        "reciver_id":contact_id,
        "message":msg,
        "datetime":datahora
    }
    msg = "MET=REG&SND="+ip_privado+"&RES=NovaMensagem()&CNTT=json--H "+json.dumps(msg)
    resp = validaResposta(enviaRequisicao(msg))
    if resp["header"]["STATUS"] == "OK" and resp["body"][0] == "MIS":
        print(f"{alignCenter()}Mensagem enviada com sucesso")
    else:
        print(f"{alignCenter()}Erro ao enviar mensagem")

def alignCenter():
    return "                                        "

#threading.Thread(target=exibir_mensagens, daemon=True).start()
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
            username = input("Usuario : ")
            password = input("Senha: ")    

            print(f"{alignCenter()}Solicitando authenticacao de usuario")           
            time.sleep(1)      

            try:
                loginData = login(username,password)
            
                if loginData["body"][0] != "NEG" and loginData["body"][0] != "RNF":      
                    limpaTela()
                    print("") 
                    print(f"{alignCenter()}Usuario Autorizado")      
                    print("")            
                    time.sleep(1)      

                    user_id = loginData["body"][0]
                    contatos_salvos = contatos(user_id)

                    while True:
                        limpaTela()
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
                                limpaTela()
                                print("")
                                print("")         
                                print(f"""
                                        -----------------------------
                                        App de Mensagens - {username}
                                        -----------------------------
                                        """)                       
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
                                        limpaTela()     
                                        contact_id = opcao 

                                        script_dir = os.path.dirname(os.path.abspath(__file__))
                                        messanger_path = os.path.join(script_dir, "messanger.py")    
                                        script_dir = script_dir.replace('\\', '/')
                                        print(f"{script_dir}")
                                                                                                
                                        process = subprocess.Popen([
                                            "start",
                                            "cmd",
                                            "/K",
                                            "python",
                                            "-c",
                                            f"import sys; sys.path.append('{script_dir}');from messanger import *;app = Messager('{str(user_id)}','{str(username)}','{str(contact_id)}');app.run();"],
                                            shell=True)

                                        while True:                                                                                       

                                            print("")
                                            print(f"{alignCenter()}newm - Nova mensagem")
                                            print(f"{alignCenter()}quit - voltar")
                                            option = input(f"{alignCenter()}Opção: ")
                                            
                                            match option:
                                                case "newm":
                                                    enviarMensagem(user_id,contact_id)
                                                case "quit":
                                                    if process.poll() is None:
                                                        process.terminate()                                                    
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



    
    
        



