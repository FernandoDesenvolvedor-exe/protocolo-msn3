#
# Servidor
#

from manager import *
from socket import *
import json

# variaveis globais
requestManager = RequestManager()

usuarios = list([
    {"username": "Fernando", "password":"123", "IP": None},
    {"username": "Felipe","password":"123", "IP": None},
    {"username": "Guilherme","password":"123", "IP": None},
    {"username": "Andressa","password":"123", "IP": None}
])

#[(x,y) for x in [1,2,3]   ]

conversas = {
    "0":{
        "1":{
            "enderecado":"Felipe",
            "conversa":{
                "0":["Oi mano","2024-12-25 10:33:03","lida"],
                "2":["Tudo bem?","2024-12-25 10:33:58","lida"],
            }
        },
        "2":{
            "enderecado":"Guilherme",
            "conversa":{
                "0":["Oi mano","2024-12-25 11:30:00","lida"],
                "2":["Ja buscou a parada la?","2024-12-25 11:35:30","lida"]              
            }
        },
        "3":{
            "enderecado":"Andressa",
            "conversa":{
                "0":["Oi vida","2024-12-25 20:01:03","lida"],
                "2":["Como ta a aula?","2024-12-25 20:02:14","lida"]
            }
        }
    },
    "1":{
        "0":{
            "enderecado":"Fernando",
            "conversa":{
                "1":["Aew cara","2024-12-25 10:33:40","lida"],
                "3":["Tudo certo aqui mano","2024-12-25 10:34:26","lida"]
            }
        },
        "2":{
            "enderecado":"Guilherme",
            "conversa":{
                "0":["Oi mano","2024-12-25","11:30:00","lida"],
                "2":["Ja buscou a parada la?","2024-12-25","11:35:30","lida"],
            }
        }
    },
    "2":{
        "0":{
            "enderecado":"Fernando",
            "conversa":{
                "1":["Fala","2024-12-25 11:33:40","lida"],
                "3":["Sim","2024-12-25 11:36:20","lida"]
            }
        },
        "1":{
            "enderecado":"Felipe",
            "conversa":{
                "1":["Fala","2024-12-25","11:33:40","lida"],
                "3":["Sim","2024-12-25","11:36:20","lida"]
            }
        } 
    },
    "3":{
        "0":{
            "enderecado":"Fernando",
            "conversa":{
                "1":["Oii","2024-12-25 20:01:15","lida"],
                "3":["Entediante","2024-12-25 20:02:23","lida"]
            }
        }        
    }
}

requestManager.generateSocketListener()

while True:
    #
    # Recebe a mensagem
    #
    request = requestManager.catchDecodedRequest()

    print(f"Recebido: {requestManager.messageCaught.decode()}")

    try:       

        match request.met:
            case "AUTH":
                match request.res:
                    case "Login":
                        username = request.res_params[0]
                        password = request.res_params[1]
                        user_id = 0

                        for n,user in enumerate(usuarios,start=0):
                            if user.get("username") == username:
                                user_acc = user
                                user_id = n
                                break

                        if user_acc != None:
                            if user_acc.get("password") == password:
                                user_acc["IP"] = requestManager.addressCaught[0]
                                user = {"id":user_id}

                                preparedResponse = Response(
                                    snd="SERVER",
                                    status="OK",
                                    body=user
                                )

                                del user
                                del username
                                del password
                                del user_id
                                del user_acc
                                del n
                            else:
                                response = "SND=SERVER&STATUS=OK--RESP NEG"
                        else:
                            response = "SND=SERVER&STATUS=OK--RESP NEG"
                    case "Logout":
                        raise Exception
                    case _:
                        response = "SND=SERVER&STATUS=ERR--RESP RNF"
            case "CDS":
                match request.res:
                    case "Contatos":
                        id = str(request.res_params[0])
                        
                        if conversas.get(id) != None:
                            try:                             
                                users = {}
                                n = 0

                                for talked_to_id in conversas.get(id):
                                    contactName = conversas.get(id).get(talked_to_id).get("enderecado")
                                    ip_atual = usuarios.get(contactName).get("IP")

                                    if ip_atual == "0": 
                                        state = "OFF" 
                                    else: 
                                        state = "ON"                                            

                                    users[n] = {
                                        "id": talked_to_id,
                                        "name": contactName,
                                        "status": state 
                                    }

                                    n += 1

                                preperadResponse = Response(
                                    body=json.dumps(users),
                                    snd="SERVER",
                                    status="OK"
                                )

                            except IndexError:
                                print("deu ruim pai")
                                

                            response = "SND=SERVER&STATUS=OK&CNTT=json--RESP "+json.dumps(users)
                        else:
                            response = "SND=SERVER&STATUS=OK--RESP  NUF"
                    case "Conversas":
                        id_user = data["header"]["RESPR"][0]
                        id_contact = data["header"]["RESPR"][1]
                        
                        if conversas.get(id_user) != None:
                            if conversas[id_user].get(id_contact) != None:                              

                                messages_sent = conversas[id_user][id_contact]
                                messages_received = conversas[id_contact][id_user]
                                chat = {"messages_sent":messages_sent,"messages_received":messages_received}

                            else: 
                                chat = {"error":"CNE"} #Contato não encontrado
                        else:
                            chat = {"error":"UNE"} #Usuario não encotrado
                        
                        response = "SND=SERVER&STATUS=OK&CNTT=json--RESP "+json.dumps(chat,indent=None,separators=(',', ':'))
                    case "UltimaMensagem":
                        if data["header"].get("RESPR") != None:
                            user_id = data["header"]["RESPR"][0]
                            contact_id = data["header"]["RESPR"][1]

                            for indice in conversas[user_id][contact_id]["conversa"]:
                                sender_last_id = int(indice)

                            for indice in conversas[contact_id][user_id]["conversa"]:
                                receiver_last_id = int(indice)        

                            message = {
                                "name": "",
                                "message": "",
                                "datetime": "",
                                "status": ""
                            }                    

                            if sender_last_id > receiver_last_id:      
                                message["name"] = conversas[contact_id][user_id]["enderecado"]
                                message["message"] = conversas[user_id][contact_id]["conversa"].get(str(sender_last_id))[0]
                                message["datetime"] = conversas[user_id][contact_id]["conversa"].get(str(sender_last_id))[1]
                                message["status"] = conversas[user_id][contact_id]["conversa"].get(str(sender_last_id))[2]

                                if message["status"] == "nova":
                                    conversas[user_id][contact_id]["conversa"][str(sender_last_id)][2] = "lida"
                            else:                                
                                message["name"] = conversas[user_id][contact_id]["enderecado"]
                                message["message"] = conversas[contact_id][user_id]["conversa"].get(str(receiver_last_id))[0]
                                message["datetime"] = conversas[contact_id][user_id]["conversa"].get(str(receiver_last_id))[1]
                                message["status"] = conversas[contact_id][user_id]["conversa"].get(str(receiver_last_id))[2]

                                if message["status"] == "nova":
                                    conversas[contact_id][user_id]["conversa"][str(receiver_last_id)][2] = "lida"  # altera valor de para mensagem lida
                           
                            response = "SND=SERVER&STATUS=OKCNTT=json--RESP "+json.dumps(message)

                            del message
                        else:
                            response = "SND=SERVER&STATUS=OK--RESP PNNE"
                    case _:
                        response = "SND=SERVER&STATUS=OK--RESP RNF"
            case "REG":
                match resource:
                    case "NovaMensagem": 
                        if len(data["body"]) > 0:    
                            try:
                                
                                data["body"] = json.loads(data["body"][0]) 

                                id_sender = data["body"]["sender_id"]
                                id_receiver = data["body"]["reciver_id"]
                                message = data["body"]["message"]
                                date_time = data["body"]["datetime"]

                                new_message = [message, date_time, "nova"]
                                
                                sender_last_id = 0
                                receiver_last_id = 0
                                new_id = 0

                                for indice in conversas[id_sender][id_receiver]["conversa"]:
                                    sender_last_id = int(indice)

                                for indice in conversas[id_receiver][id_sender]["conversa"]:
                                    receiver_last_id = int(indice)

                                if sender_last_id > receiver_last_id:
                                    new_id = sender_last_id+1
                                elif receiver_last_id > sender_last_id:
                                    new_id = receiver_last_id+1

                                conversas[id_sender][id_receiver]["conversa"][str(new_id)] =  new_message

                                response = "SND=SERVER&STATUS=OK--RESP MIS" # Mensagem inserida com sucesso

                            except IndexError:
                                response = "SND=SERVER&STATUS=OK--RESP PNNE" # parametro necessario não encontrado
                            except json.JSONDecodeError as e:
                                print(e)
                                response = "SND=SERVER&STATUS=OK--RESP JMF" # Json mal formatado
                        else:
                            response = "SND=SERVER&STATUS=OK--RESP PNNE" # parametro necessario não encontrado
                    case _:
                        response = "SND=SERVER&STATUS=OK--RESP RNF" # recurso não encontrado
            case _:
                response = "SND=SERVER&STATUS=OK--RESP MNS" # metodo não encontrado

    except Exception as e:
        print(e)
        response = "SND=SERVER&STATUS=ERR--RESP UE" # erro inesperado

    requestManager.answerRequest(preparedResponse)
    print("Respondido :",preparedResponse.formatedResponse)
    print("")