from socket import *
from datetime import datetime
import json
import time

class RequestManager:
    def __init__(self) -> None:
        self.private_ip = self.getPrivateIp()
        self.private_door = 12000
        self.server_ip = None
        self.server_door = 12000
        self.msn3HeaderParams = ["AUTH","CDS","REG"]

    def parseMsn3Request(self,request):
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
            sender_data = requestData["header"]["SND"].split("/")
            requestData["header"]["SND"] = sender_data[0]
            requestData["header"]["DOOR"] = sender_data[1]

            for method in self.msn3HeaderParams:
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
    
    def sendMsn3Request(self,address,door,met,res,res_params = None,msg = None,cntt = None):
        
        if res_params is None:
            res_params = "()"
        else:
            res_params = json.dumps(res_params)
            res_params = res_params.replace("[","(").replace("]",")")
        
        if msg is None:
            msg = ""

        match cntt:
            case "json":
                msg = json.dumps(msg)
            case "str":
                msg = str(msg)
            case None|_:
                cntt = "None"

        try:
            request = f"MET={met}&SND={self.private_ip}/{self.private_door}&RES={res}{res_params}&CNTT{cntt}--H {msg}"

            socketTuple = (address, door)
            msg = msg.encode()
            socCli = socket( AF_INET, SOCK_STREAM )
            socCli.connect( socketTuple )
            socCli.send(request)
            resp = socCli.recv(1024)
            socCli.close()

            resp = self.parseMsn3Request(resp)
            if resp["STATUS"] == "OK":
                time.sleep(2)
                return resp
            else:
                time.sleep(2)
                raise ConnectionError(f"{resp["body"]}")
                

        except Exception as e:
            print(e)

            time.sleep(2)
            return False
    
    def validaResposta(self,resposta):
        if resposta["header"]["STATUS"] == "ERR":
            raise ConnectionError(resposta["body"])

        if resposta["header"].get("CNTT") != None and resposta["header"].get("CNTT") == "json":
            resposta["body"] = json.loads(resposta["body"][0])
            
        return resposta
      
    def setServerIp(self,ip):
        self.server_ip = ip

    def setServerDoor(self,door):
        self.server_door = door

    def setReceiverId(self,id_receiver):
        self.id_receiver = id_receiver

    def getPrivateIp(self):        
        try:
            # Cria um socket de conexão para determinar o IP privado
            with socket(AF_INET, SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Conecta a um servidor externo (Google DNS)
                ip = s.getsockname()[0]    # Obtém o IP da máquina
            return ip
        except Exception as e:
            return f"Erro ao obter IP privado: {e}"
        
    def getPrivateDoor(self):
        return self.private_door


class ChatManager:
    def __init__(self,user_id=None,id_receiver=None,user_name=None) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.id_receiver = id_receiver

    def conversas(self):
        msg = "MET=CDS&SND="+self.getPrivateIp()+"&RES=Conversas("+str(self.user_id)+","+self.id_receiver+")--H "
        return self.validaResposta(self.enviaRequisicao(msg))
    
    def runChat(self,requestManager):
        chat = self.conversas()["body"]
        contact_id = self.id_receiver
        contact_name = chat.get("messages_sent").get("enderecado")
    
        chat2 = chat.get("messages_received")
        chat = chat.get("messages_sent")

        chat2.pop("enderecado")
        chat.pop("enderecado")
        
        for index in chat2.get("conversa"):
            chat2.get("conversa").get(index).append(contact_name)

        for index in chat.get("conversa"):
            chat.get("conversa").get(index).append(self.name_sender)

        chat.get("conversa").update(chat2.get("conversa"))
        del chat2
        chat = chat["conversa"]

        print(len(chat))
        chat = dict(sorted(chat.items()))

        print("-------------------------------------------------")
        print(f"Conversa com {contact_name} código({contact_id})")
        print("-------------------------------------------------")       

        for index in chat:
            print(f"""{chat[index][3]}: {chat[index][0]} -- {chat[index][1]}""")

        while True:
            self.receberUltimaMensagem()
            time.sleep(0.5)
    
    def receberUltimaMensagem(self):
        try:
            socketServidor = socket(AF_INET, SOCK_STREAM)
            socketListener = ('',12000)
            socketServidor.bind( socketListener )
            socketServidor.listen(True)
            conexao, endereco = socketServidor.accept()
            mensagem = conexao.recv(1024)
            mensagem = mensagem.decode()       

            msg = "MET=CDS&SND="+self.getPrivateIp()+"&RES=UltimaMensagem("+str(self.user_id)+","+str(self.id_receiver)+")--H "
            mensagem = self.validaResposta(self.enviaRequisicao(msg))
            mensagem = json.loads(mensagem["body"][0]) 

            if(mensagem["status"]) == "nova":
                print(f"{mensagem["name"]}: {mensagem["message"]} -- {mensagem["datetime"]}")
            else:
                pass
        except ConnectionError:
            pass
   
    def chatInputStream(self):
        while True:
            msg_input = input("digite quitapp para sair: ")
            
            if msg_input is "quitapp":
                break
            else:
                msg = {
                    "sender_id": self.user_id,
                    "reciver_id":self.id_receiver,
                    "message":msg_input,
                    "datetime": datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                }
                msg = json.dumps(msg)
                self.sendMsn3Request(address=self.server_ip,door=self.server_door,msg=msg,cntt="json",met="REG",res="EnviarMensagem",res_params=[self.user_id, self.id_receiver])
   
    def setUserId(self,user_id):        
        self.user_id = user_id

    def setUserName(self,name):
        self.user_name = name