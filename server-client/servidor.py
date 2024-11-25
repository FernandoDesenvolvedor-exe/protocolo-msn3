#
# Servidor
#

from socket import *

socketServidor = socket(AF_INET, SOCK_STREAM)
tuplaEscuta = ('',12000)
socketServidor.bind( tuplaEscuta )
socketServidor.listen(True)


#               [conversas]
conversas = {
    "191.54.26.241":{
        "191.54.26.245":{
            "Fernando":[["Oi mano","2024-12-25","10:33:03"],["Tudo bem?","2024-12-25","10:33:58"]],
            "Felipe":[["Aew cara","2024-12-25","10:33:40"],["Tudo certo aqui mano","2024-12-25","10:34:26"]]
        },
        "191.54.26.241-191.54.26.145":{
            "Fernando":[["Oi mano","2024-12-25","11:30:00"],["Ja buscou a parada la?","2024-12-25","11:35:30"]],
            "Guilherme":[["Fala","2024-12-25","11:33:40"],["Sim","2024-12-25","11:36:20"]]
        },
        "191.54.26.241-191.54.26.345":{
            "Fernando":[["Oi vida","2024-12-25","20:01:03"],["Como ta a aula?","2024-12-25","20:02:14"]],
            "Andressa":[["Oii","2024-12-25","20:01:15"],["Entediante","2024-12-25","20:02:23"]]
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

    request = mensagem.split()
    header = request[0].replace("HEAD--","").split("&")
    body = request[1].replace("BODY--","").split("&")

    match header[2]:
        case "CONSULTA":
            response = conversas.get(header[0])
                
            if(header[1] != "0"):
                response = response.get(header[1])

            print(response)
            
            break
        case _:
            print("Metodo não reconhecido")
        
    print(header)
    print(body)

    break
    
