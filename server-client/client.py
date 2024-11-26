def conversas(userid):
    msg = ip_publico+"&CONSULTA&Conversas--H "+str(userid)+""
    msg = msg.encode()
    socCli = socket( AF_INET, SOCK_STREAM )
    socCli.connect( tuplaDestino )
    socCli.send(msg)
    resp = socCli.recv(1024)
    resp = resp.decode()
    socCli.close()

    return resp

def login(username,password):
    msg = ip_publico+"&AUTH&Login--H "+username+"&"+password
    msg = msg.encode()
    socCli = socket( AF_INET, SOCK_STREAM )
    socCli.connect( tuplaDestino )
    socCli.send(msg)
    resp = socCli.recv(1024)
    socCli.close()
    
    return resp.decode() 

# O PROTOCOLO SERA COMPOSTO POR CABEÇALHO COM INFORMAÇÕES DE QUEM ENVIOU
from socket import *
import requests
import json
 
tuplaDestino = ('localhost',12000) 
ip_publico = requests.get('https://api.ipify.org/').text 

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

    opcao = int(input("Escolha uma opcao"))
    match opcao:
        case 1:
            #username = input("Usuario : ")
            #password = input("Senha: ")

            username = "Fernando"
            password = "123"            

            print("Solicitando authenticacao de usuario")            

            resp = login(username,password)
            resp = resp.split("--H")
            resp_h = resp[0].split("&")
            resp_b = resp[1].strip().split("&")
            
            if resp_h[3] == "OK":
                if resp_b != "NEG" and resp_b != "RNF":
                        userid = resp_b[0]

                        while True:
                            print("")
                            print("")
                            print("-----------------------------")
                            print("App de Mensagens - "+username)
                            print("-----------------------------")
                            print("")
                            print("")
                            resp = conversas(userid).strip()
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

                                    for users in chat:
                                        print(users[0]+": "+users[1]+" "+users[2])
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



    
    
        



