# O PROTOCOLO SERA COMPOSTO POR CABEÇALHO COM INFORMAÇÕES DE QUEM ENVIOU
from socket import *
import requests
 
tuplaDestino = ('localhost',12000) 
ip_publico = requests.get('https://api.ipify.org/').text 
 
print("")
print("")
print("-----------------------------")
print("App de Mensagens - Conversas")
print("-----------------------------")
print("")
print("")
login = input("Usuario : ")
senha = input("Senha: ")
 
msg = "HEAD--Login BODY--user="+login+"pass="+senha

msg = msg.encode()

print("Solicitando conversas para o servidor")
                 
socCli = socket( AF_INET, SOCK_STREAM )
socCli.connect( tuplaDestino )
socCli.send(msg)
resp = socCli.recv(1024)
resp = resp.decode()
socCli.close()         
op = input("Opcao : ")
