# importacao de bibliotecas
import json
import socket
from arvore import Calculadora


# executa as operacoes basicas de soma, subtracao, divisao e multiplicacao
def executar_operacao(operacao, op1, op2):
    # aplicar a operacao nos nós atuais
            if operacao == '+':
                return op1 + op2
            elif operacao == '-':
                return op1 - op2
            elif operacao == '*':
                return op1 * op2
            elif operacao == '/':
                if op2 == 0:
                    raise ZeroDivisionError("Divisao por zero.")
                return op1 / op2
            elif operacao == '**':
                return op1 ** op2
            else:
                raise ValueError("Operacao nao reconhecida {operacao}.")

# interpreta o json recebido e devolve o resutlado formatado
def processar_requisicao(dados_recebidos):
    tipo = dados_recebidos.get("tipo")
    
    # requisicao de operacao individual
    if tipo == "operacao":
        operacao = dados_recebidos.get("operacao")
        op1 = float(dados_recebidos.get("op1"))
        op2 = float(dados_recebidos.get("op2"))
        resultado = executar_operacao(operacao,op1,op2)
        return {"status": "ok", "resultado": resultado}
    elif tipo == "expressao_arvore":
        dados_arvore = dados_recebidos.get("arvore")
        # faz a reconstrucao da arvore a partir do dicionar
        arvore_reconstruida = Calculadora.de_dict(dados_arvore)
        # servidor resolve a expressao recursivamente
        resultado = Calculadora.calcular_arvore(arvore_reconstruida)
        return {"status": "ok", "resultado": resultado}
    else:
        return {"status": "erro", "mensagem": "Tipo de requisicao invalida"}
    
def inicia_servidor(host='192.168.5.165', porta=9092):
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor_socket.bind((host, porta))
    servidor_socket.listen(5)
    print(f"[*] Servidor da Calculadora aguardando conexões em {host}:{porta}...")
    
    while True:
        cliente_socket, endereco = servidor_socket.accept()
        try:
            # Recebe o buffer da mensagem (tamanho suficiente para os payloads JSON)
            dados_brutos = cliente_socket.recv(4096).decode('utf-8')
            if dados_brutos:
                mensagem = json.loads(dados_brutos)
                try:
                    resposta = processar_requisicao(mensagem)
                except Exception as e:
                    resposta = {"status": "erro", "mensagem": str(e)}

                # Envia de volta o JSON codificado
                cliente_socket.sendall(json.dumps(resposta).encode('utf-8'))
        finally:
            cliente_socket.close()
            
if __name__ == "__main__":
    inicia_servidor()