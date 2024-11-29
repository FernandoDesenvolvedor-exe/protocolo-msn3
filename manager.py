from socket import *
from datetime import datetime
import json
import time

class Response:
    def __init__(self,snd:str=None,status:str=None,body:dict|str="",cntt:str = "json"):        
        
        self.snd = snd
        self.status = status
        self.body = body
        self.cntt = cntt
        
        match cntt:
            case "json":
                body = json.dumps(body)
            case 'str':
                body = str(body)
            case None:
                raise ValueError("Request-prepareResponse-4")

        self.formatedResponse =  f"SND={snd}&STATUS={status}&CNTT={cntt}--RESP {body}"

    def setAttributesByFormatedResponse(self):
        request = self.formatedResponse.split("--RESP ")
        header = request[0].strip().split("&")
        body = request[1].strip()

        headerDict = {"header": {}}

        for data in header:
            key_data = data.split("=")
            headerDict["header"][key_data[0]] = key_data[1]

        if headerDict["header"].get("CNTT") != None:
            match headerDict["header"].get("CNTT"):
                case "json":
                    self.body = body = json.loads(body)
                    self.cntt = "json"
                case "str":
                    self.body = str(body)
                    self.cntt = "str"
                case _:
                    self.cntt = "NS"
        else:
            self.cntt = "None"

        self.snd = headerDict["header"].get("SND")
        self.status = headerDict["header"]["STATUS"]

    @property
    def formatedResponse(self):
        return self._formatedResponse
    
    @formatedResponse.setter
    def formatedResponse(self,newResponse):
        self._formatedResponse = newResponse

    @property
    def snd(self):
        return self._snd
    
    @snd.setter
    def snd(self,newSnd):
        self._snd = newSnd

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self,newStatus):
        self._status = newStatus

    @property
    def body(self):
        return self._body
    
    @body.setter
    def body(self,newBody):
        self._body = newBody

    @property
    def cntt(self):
        return self._cntt
    
    @cntt.setter
    def cntt(self,newCntt):
        self._cntt = newCntt

class Request:
    def __init__(self,met:str,destiny_door:str=None,destiny_addr:str=None,res:str = None,res_params:tuple = None,body = None,cntt = None):
        self.destiny_addr = destiny_addr
        self.destiny_door = destiny_door
        self.met = met
        self.res = res
        self.res_params = res_params
        self.body = body
        self.cntt = cntt

    def prepareRequestResponse(self,snd:str,status:str,body:dict|str="",cntt:str = "json"):
        if not snd:
            raise ValueError("Request-prepareResponse-1")
        if not status:
            raise ValueError("Request-prepareResponse-2")
        if body == None:
            raise ValueError("Request-prepareResponse-3")
        
        match cntt:
            case "json":
                body = json.dumps(body)
            case 'str':
                body = str(body)
            case None:
                raise ValueError("Request-prepareResponse-4")

        return f"SND={snd}&STATUS={status}&CNTT={cntt}--RESP {body}"

    def prepareRequestMessage(self):
        if not self.origin_addr:
            raise ValueError("propriedade origin_addr não pode estar vazia")
        
        if not self.origin_door:
            raise ValueError("propriedade origin_door não pode estar vazia")
        
        if not self.met:
            raise ValueError("propriedade met não pode estar vazio")

        if not self.res_params and self.res:
            self.res_params = "()"
        elif not self.res_params and not self.res:
            self.res_params = ""
        else:
            self.res_params = json.dumps(self.res_params).replace("[","(").replace("]",")").replace('"','')

        if not self.body:
           self.body = ""

        match self.cntt:
            case "json":
               self.body = json.dumps(self.body)
            case "str":
               self.body = str(self.body)
            case None:
                self.cntt = "NS"
            case _:
                raise ValueError("cnnt (content type) deve ser nome de uma classe valida para a requisição")
        
        return f"MET={self.met}&SND={self.origin_addr}/{self.origin_door}&RES={self.res}{self.res_params}&CNTT={self.cntt}--H {self.body}"

    @property
    def destiny_addr(self):
        return self._destiny_addr

    @property
    def destiny_door(self):
        return self._destiny_door

    @property
    def origin_addr(self):
        return self._origin_addr

    @property
    def origin_door(self):
        return self._origin_door

    @property
    def address(self):
        return self._address
    
    @property
    def body(self):
        return self._body
    
    @property
    def door(self):
        return self._door
    
    @property
    def met(self):
        return self._met  
    
    @property
    def res(self):
        return self._res
   
    @property
    def res_params(self):
        return self._res_params
    
    @property
    def cntt(self):
        return self._cntt
    
    @destiny_addr.setter
    def destiny_addr(self, new_destiny_addr):
        self._destiny_addr = new_destiny_addr

    @destiny_door.setter
    def destiny_door(self,new_destiny_door):
        self._destiny_door = new_destiny_door

    @origin_door.setter
    def origin_door(self,new_origin_door):
        self._origin_door = new_origin_door

    @origin_addr.setter
    def origin_addr(self,new_origin_addr):
        self._origin_addr = new_origin_addr

    @address.setter
    def address(self,new_address):
        if new_address is not str:
            raise TypeError("address deve ser str")        
        self._address = new_address
    
    @body.setter
    def body(self,new_body:dict|str):
        self._body = new_body

    @door.setter
    def door(self,new_door):
        if not new_door:
            raise ValueError("MSG não pode ser vazio")        
        self._door = new_door
        
    @res.setter
    def res(self,new_res):      
        self._res = new_res
    
    @res_params.setter
    def res_params(self,new_res_params):     
        self._res_params = new_res_params
    
    @met.setter
    def met(self,new_met):
        if not new_met:
            raise ValueError("met não pode ser vazio")        
        self._met = new_met
    
    @cntt.setter
    def cntt(self,new_cntt):    
        self._cntt = new_cntt
    
class RequestManager:
    def __init__(self,lineEndIp: str = None,) -> None:
        self.myIp = self.getPrivateIp()
        self.myDoor = 12000
        self.lineEndIp = lineEndIp
        self.lineEndDoor = 12000
        self.msn3ReqParams = ["AUTH","CDS","REG"]
        self.socket = socket(AF_INET, SOCK_STREAM)        

    def generateSocketListener(self):
        tubleListener = (self.getPrivateIp(),self.getPrivateDoor())
        self.socket.bind( tubleListener )
        self.socket.listen(True)

    def catchDecodedRequest(self):
        self.connection, self.addressCaught = self.socket.accept()
        self._messageCaught = self.connection.recv(1024)
        return self.parseToRequest(self._messageCaught.decode())

    def answerRequest(self,preperadResponse:Response):
        response = preperadResponse.formatedResponse
        self.connection.send(response.encode())
        self.connection.close()

    def parseToRequest(self,message):
        if message.find("--H") != -1:
            message = message.split("--H")
        elif message.find("--RESP"):
            message = message.split("--RESP")

        resp_h = message[0].strip().split("&")
        resp_b = message[1].strip().split("&")

        requestData = {"header": {}}

        for data in resp_h:
            key_data = data.split("=")
            requestData["header"][key_data[0]] = key_data[1]

        try:
            sender_data = requestData["header"]["SND"].split("/")
            
            index = 1

            if 0 <= index < len(sender_data):
                requestData["header"]["SND"] = sender_data[index]                
                requestData["header"]["DOOR"] = sender_data[0]
            else:
                requestData["header"]["SND"] = sender_data[0]  
            
            if requestData["header"].get("RES") != None: 
                res_param = requestData["header"]["RES"].replace(")","&").replace("(","&").split("&")
                res_param.pop(2)
                res =  res_param[0]
                params = str(res_param[1])

                if params != '':
                    params = params.split(",")
                    params = [param.strip() for param in params]

                requestData["header"]["RES"] = res
                requestData["header"]["RESPR"] = params
        except KeyError as e:
            print(e)
            requestData["header"]["RES"] = ""
            requestData["header"]["RESPR"] = ""    
        
        if requestData["header"]["CNTT"] == "json":
            requestData["body"] = json.loads(resp_b[0])
        else:
            requestData["body"] = resp_b[0]


        request = Request(
            destiny_addr=self.addressCaught[0],
            destiny_door=self.addressCaught[1],
            met=requestData["header"]["MET"],
            res=requestData["header"]["RES"],
            res_params=requestData["header"]["RESPR"],
            body=requestData["body"],
            cntt=requestData["header"]["CNTT"]
        )

        return request
    
    def sendMsn3Request(self,request: Request, destiny_ip:str = None, destiny_door:int = None):
        try:
            if destiny_door == None:
                if request.destiny_door == None:
                    if self.lineEndDoor == None:
                        raise ValueError("Destino não pode estar vazio")
                    else:
                        door = self.lineEndDoor
                else:
                    door = request.destiny_door
            else:
                door = destiny_door
            
            if destiny_ip == None:
                if request.destiny_addr == None:
                    if self.lineEndDoor == None:
                        raise ValueError("Destino não pode estar vazio")
                    else:
                        ip = self.lineEndIp
                else:
                    ip = request.destiny_addr
            else:
                ip = destiny_ip

            request.origin_door = self.myIp
            request.origin_addr = self.myDoor

            preparedMessage = request.prepareRequestMessage()
            encodedMsg = preparedMessage.encode()

            try:
                socketTuple = (ip, door)
                socCli = socket( AF_INET, SOCK_STREAM )
                socCli.connect( socketTuple )
                socCli.send(encodedMsg)
                resp = socCli.recv(1024)
                socCli.close()

                response = Response()
                response.formatedResponse = resp.decode()
                response.setAttributesByFormatedResponse()

                if response.status == "OK":
                    return response
                else:
                    raise ConnectionError("Response - sendMsn3Request 379")
                    
            except ValueError as e:
                print(e)
                time.sleep(2)
                return False
        except ConnectionError as e:
            print(e)
            return False
        
    def setResponse(self,request:Request):
        self.request = request

    def validaResposta(self,resposta):
        if resposta["header"]["STATUS"] == "ERR":
            raise ConnectionError(resposta["body"])

        if resposta["header"].get("CNTT") != None and resposta["header"].get("CNTT") == "json":
            resposta["body"] = json.loads(resposta["body"][0])
            
        return resposta
      
    def setLineEndIp(self,ip):
        self.lineEndIp = ip

    def setLineEndDoor(self,door):
        self.lineEndDoor = door
    
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
        return self.myDoor

    @property
    def addressCaught(self):
        return self._addressCaught
    
    @addressCaught.setter
    def addressCaught(self,newAddress):
        self._addressCaught = newAddress

    @property
    def messageCaught(self):
        return self._messageCaught
    
    @messageCaught.setter
    def messageCaught(self,new_message_caught):
        self._messageCaught = new_message_caught

class ChatManager:
    def __init__(self,user_id=None,contact_id=None,user_name=None) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.contact_id = contact_id

    @property
    def user_id(self):
        return self._user_id
    
    @property
    def user_name(self):
        return self._user_name
    
    @property
    def contact_id(self):
        return self._contact_id
    
    @contact_id.setter
    def contact_id(self,new_contact_id):
        self._contact_id = new_contact_id

    @user_name.setter
    def user_name(self,new_name):
        self._user_name = new_name

    @user_id.setter
    def user_id(self,new_id):
        self._user_id = new_id

    def conversas(self):
        msg = "MET=CDS&SND="+self.getPrivateIp()+"&RES=Conversas("+str(self.user_id)+","+self.contact_id+")--H "
        return self.validaResposta(self.enviaRequisicao(msg))
    
    def runChat(self,requestManager):
        chat = self.conversas()["body"]
        contact_id = self.contact_id
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

            msg = "MET=CDS&SND="+self.getPrivateIp()+"&RES=UltimaMensagem("+str(self.user_id)+","+str(self.contact_id)+")--H "
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
            
            if msg_input == "quitapp":
                break
            else:
                msg = {
                    "sender_id": self.user_id,
                    "reciver_id":self.contact_id,
                    "message":msg_input,
                    "datetime": datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                }
                msg = json.dumps(msg)
                self.sendMsn3Request(address=self.lineEndIp,door=self.lineEndDoor,msg=msg,cntt="json",met="REG",res="EnviarMensagem",res_params=[self.user_id, self.contact_id])
   
    def setUserId(self,user_id):        
        self.user_id = user_id

    def setUserName(self,name):
        self.user_name = name