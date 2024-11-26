#
# Servidor
#

from socket import *
import json

socketServidor = socket(AF_INET, SOCK_STREAM)
tuplaEscuta = ('',12000)
socketServidor.bind( tuplaEscuta )
socketServidor.listen(True)


#               [usuarios]
usuarios = {"Fernando": ["123",0], "Felipe": ["321",1], "Andressa": ["456",2], "Guilherme": ["111",3]}

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

    print("Recebido :",mensagem)

    request = mensagem.split("--H")
    header = request[0].split("&")
    body = request[1].split("&")

    method = header[1]
    resource = header[2]

    match method:
        case "AUTH":
            match resource:
                case "Login":
                    user = body[0].strip()
                    password = body[1]

                    print(body)
                    
                    if(usuarios.get(user) != None):
                        usuario_login = usuarios.get(user)
                        if(usuario_login[0] == password):
                            response = "SERVER&R&json&OK--H "+str(usuario_login[1])
                        else:
                            response = "SERVER&R&json&OK--H NEG"
                    else:
                        response = "SERVER&R&json&OK--H NEG"
                case _:
                    response = "SERVER&R&json&ERR--H RNF"
        
        case "CONSULTA":
            match resource:
                case "Conversas":
                    id = body[0].strip()
                    
                    if conversas.get(id) != None:
                        response = "SERVER&R&OK&json--H "+json.dumps(conversas.get(id))
                    else:
                        response = "SERVER&R&OK--H NUF"
                                        
                case _:
                    response = "SERVER&R&ERR--H RNF"
                
        case _:
            response = "SERVER&R&ERR--H MNF"

        
    print("Respondido :", response)
    print("")
    response = response.encode()
    conexao.send(response)
    conexao.close()
