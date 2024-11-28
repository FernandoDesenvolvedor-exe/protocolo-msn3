from socket import *
from datetime import datetime
import json
import time

class Messager:    
    def __init__(self,id_sender,name_sender,id_receiver) -> None:
        self.id_sender = id_sender
        self.name_sender = name_sender
        self.id_receiver = id_receiver
        self.tuplaDestino = ('localhost',12000)
        self.msn3HeaderParams = ["AUTH","CDS","RDS"]
    
    def enviaRequisicao(self,msg):
        msg = msg.encode()
        socCli = socket( AF_INET, SOCK_STREAM )
        socCli.connect( self.tuplaDestino )
        socCli.send(msg)
        resp = socCli.recv(1024)
        socCli.close()

        return self.parseMsn3Request(resp.decode())

    def getPrivateIp(self):
        try:
            # Cria um socket de conexão para determinar o IP privado
            with socket(AF_INET, SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Conecta a um servidor externo (Google DNS)
                ip = s.getsockname()[0]    # Obtém o IP da máquina
            return ip
        except Exception as e:
            return f"Erro ao obter IP privado: {e}"
        
    def validaResposta(self,resposta):
        if resposta["header"]["STATUS"] == "ERR":
            raise ConnectionError(resposta["body"])

        if resposta["header"].get("CNTT") != None and resposta["header"].get("CNTT") == "json":
            resposta["body"] = json.loads(resposta["body"][0])
            
        return resposta

    def conversas(self):
        msg = "MET=CDS&SND="+self.getPrivateIp()+"&RES=Conversas("+str(self.id_sender)+","+self.id_receiver+")--H "
        return self.validaResposta(self.enviaRequisicao(msg))

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

    def asd():
        while True:
            print(" asd ")
            time.sleep(1)

    def run(self):
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
            msg = "MET=CDS&SND="+self.getPrivateIp()+"&RES=UltimaMensagem("+str(self.id_sender)+","+str(self.id_receiver)+")--H "
            mensagem = self.validaResposta(self.enviaRequisicao(msg))
            print(mensagem)
        except ConnectionError:
            pass

