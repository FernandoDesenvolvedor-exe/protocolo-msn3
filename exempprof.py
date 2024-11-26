import socket
import threading
import time
import queue

# Pergunta ao usuário o IP do outro computador para estabelecer a conexão
ip_destino = input("Digite o endereço IP do computador com o qual deseja conversar: ")
porta = 12345  # Define a porta que será usada para conexão (ambos os computadores devem usar a mesma porta)

# Fila para armazenar mensagens recebidas, para exibição na tela
mensagens_recebidas = queue.Queue()

# Função para receber mensagens e colocá-las na fila
def receber_mensagens():
    # Configura o socket de servidor para receber mensagens
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', porta))
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

# Função para enviar mensagens
def enviar_mensagens():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Tenta conectar até que o outro computador esteja disponível
    while True:
        try:
            client_socket.connect((ip_destino, porta))
            print("Conectado para enviar mensagens.")
            break
        except ConnectionRefusedError:
            print("O outro usuário ainda não está pronto. Tentando novamente em 3 segundos...")
            time.sleep(3)

    # Loop de envio de mensagens
    while True:
        mensagem = input("Você: ")
        client_socket.send(mensagem.encode())
        if mensagem.lower() == 'sair':
            break

    client_socket.close()

# Função para exibir as mensagens da fila, garantindo que elas apareçam imediatamente
def exibir_mensagens():
    while True:
        while not mensagens_recebidas.empty():
            print(mensagens_recebidas.get())  # Imprime cada mensagem da fila
        time.sleep(0.1)  # Aguarda um curto intervalo antes de verificar a fila novamente

# Executa as funções de receber, enviar e exibir mensagens ao mesmo tempo
threading.Thread(target=receber_mensagens, daemon=True).start()
threading.Thread(target=enviar_mensagens).start()
threading.Thread(target=exibir_mensagens, daemon=True).start()
