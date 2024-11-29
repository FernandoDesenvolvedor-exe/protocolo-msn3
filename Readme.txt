Autor: Luis Fernando Pereira
Arquitetura: client-server
Tecnologias: Python 3.13 
Bibliotecas: socket, json, datetime, requests, threading, time, queue, os, platform, subprocess, sys
Descrição: Este software serve como intermediário para conversas privadas entre usuários cadastrados na base de dados do software
Protocolo Msn3: Este protocolo é composto por um texto com duas partes separadas por um espaço, sendo elas o cabeçalho e o corpo. O cabeçalho não pode conter espaço entre os caracteres e os parâmetros devem ser nomeados em caixa alta. Cada parâmetro deve ser separado por &(e comercial). Funções passadas no cabeçalho devem conter parênteses e os parâmetros das funções devem conter , (virgula) para separar os argumentos passados. O cabeçalho deve terminar com --H,
enquanto o corpo da requisição termina com --B. O corpo da requisição pode ser feito no formato que quiser, desde que seja especificado no parâmetro CNTT. As requisições também devem vir com o ip privado e a porta de escuta de quem mandou.

	OS parâmetros do cabeçalho são:
		MET -> método utilizado
		SND -> Quem enviou a requisição
		RES -> Recurso que a requisição deseja usar
		RESPR -> Paramtros do recurso
		CNTT -> Tipo de formatação utilizada no corpo da 			uisição
		
		

Para rodar este projeto, é necessário apenas o python 3.13