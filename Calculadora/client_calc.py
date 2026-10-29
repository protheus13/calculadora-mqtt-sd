# Cliente da calculadora

#importacoes de bibliotecas

import socket
import json
from arvore import Calculadora


HOST_PADRAO = '192.168.5.165'
PORTA_PADRAO = 9092

def enviar_mensagem(mensagem, host=HOST_PADRAO, porta=PORTA_PADRAO):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, porta))
        payload_bytes = json.dumps(mensagem).encode('utf-8')
        s.sendall(payload_bytes)
        
        resposta_bytes = s.recv(4096)
        return json.loads(resposta_bytes.decode('utf-8'))
    
def resolver_client_rpc(no):
    if no.valor is not None:
        return no.valor
    valor_esq = resolver_client_rpc(no.left)
    valor_dir = resolver_client_rpc(no.right)
    
    mensagem = {
        "tipo": "operacao",
        "operacao": no.operacao,
        "op1": valor_esq,
        "op2": valor_dir
    }
    
    resposta = enviar_mensagem(mensagem)
    
    if resposta.get("status") == "ok":
        return resposta.get("resultado")
    else:
        raise RuntimeError(f"Erro no servidor: {resposta.get('mensagem')}")
    
def resolver_servidor_arvore_completa(no_raiz):
    dados_arvore = Calculadora.para_dict(no_raiz)
    mensagem = {
        "tipo": "expressao_arvore",
        "arvore": dados_arvore
    }
    
    resposta = enviar_mensagem(mensagem)
    
    if resposta.get("status") == "ok":
        return resposta.get("resultado")
    else:
        raise RuntimeError(f"Erro no servidor {resposta.get('mensagem')}")
    
def menu():
    print("=" * 50)
    print("      CALCULADORA DISTRIBUÍDA - AT03")
    print("=" * 50)
    print("1. Calcular Expressão - Abordagem 1 (Decomposição no Cliente)")
    print("2. Calcular Expressão - Abordagem 2 (Resolução no Servidor)")
    print("3. Operação Atómica Direta (ex: 10 + 20)")
    print("4. Sair")
    print("=" * 50)


if __name__ == "__main__":
    while True:
        menu()
        opcao = input("Selecione uma opção (1-4): ").strip()

        if opcao == "4":
            print("A encerrar o cliente...")
            break

        if opcao in ("1", "2"):
            expressao = input("\nDigite a expressão matemática (ex: ((10+2)*4)): ").strip()
            if not expressao:
                continue

            try:
                # O cliente utiliza a Calculadora para criar a árvore sintática
                raiz = Calculadora.criar_arvore_expressao(expressao)

                if opcao == "1":
                    print("[*] A calcular via Abordagem 1 (várias chamadas remotas)...")
                    resultado = resolver_client_rpc(raiz)
                else:
                    print("[*] A calcular via Abordagem 2 (envio da árvore em JSON)...")
                    resultado = resolver_servidor_arvore_completa(raiz)

                print(f"\n=> Resultado: {resultado}\n")

            except Exception as erro:
                print(f"\n[!] Falha no processamento: {erro}\n")

        elif opcao == "3":
            try:
                op1 = float(input("Digite o primeiro número (o1): "))
                operacao = input("Digite a operação (+, -, *, /): ").strip()
                op2 = float(input("Digite o segundo número (o2): "))

                msg = {"tipo": "operacao", "operacao": operacao, "op1": op1, "op2": op2}
                resp = enviar_mensagem(msg)

                if resp.get("status") == "ok":
                    print(f"\n=> Resultado: {resp.get('resultado')}\n")
                else:
                    print(f"\n[!] Erro no servidor: {resp.get('mensagem')}\n")
            except Exception as erro:
                print(f"\n[!] Entrada inválida: {erro}\n")

        else:
            print("Opção inválida, tente novamente.\n")  