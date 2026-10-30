"""
Cliente JSON-RPC 2.0 para a Calculadora Distribuída (AT03).
Demonstra as duas abordagens:
1. Decomposição local com requisições JSON-RPC atómicas.
2. Envio da árvore de expressão em JSON-RPC para cálculo remoto.
"""

import socket
import json
from arvore import Calculadora


HOST_PADRAO = "192.168.5.165"
PORTA_PADRAO = 9094
_request_id = 0


def proximo_id():
    """Gera um id incremental para cada requisição JSON-RPC."""
    global _request_id
    _request_id += 1
    return _request_id


def chamar_jsonrpc(metodo, params, host=HOST_PADRAO, porta=PORTA_PADRAO):
    """Empacota a requisição no envelope JSON-RPC 2.0, envia e processa a resposta."""
    msg_id = proximo_id()
    payload = {
        "jsonrpc": "2.0",
        "method": metodo,
        "params": params,
        "id": msg_id
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, porta))
        s.sendall(json.dumps(payload).encode("utf-8"))
        resposta_bytes = s.recv(4096)
        resposta = json.loads(resposta_bytes.decode("utf-8"))

    if "error" in resposta:
        erro = resposta["error"]
        raise RuntimeError(f"Erro JSON-RPC [{erro.get('code')}]: {erro.get('message')}")

    return resposta.get("result")


# -------------------------------------------------------------
# Abordagem 1: Decomposição local com JSON-RPC atómico
# -------------------------------------------------------------
def resolver_no_cliente_jsonrpc(no):
    if no.valor is not None:
        return no.valor

    val_esq = resolver_no_cliente_jsonrpc(no.left)
    val_dir = resolver_no_cliente_jsonrpc(no.right)

    mapa_metodos = {
        '+': 'somar',
        '-': 'subtrair',
        '*': 'multiplicar',
        '/': 'dividir',
        '**': 'potencia'
    }

    metodo = mapa_metodos.get(no.operacao)
    if not metodo:
        raise ValueError(f"Operador desconhecido: {no.operacao}")

    params = {"op1": val_esq, "op2": val_dir}
    return chamar_jsonrpc(metodo, params)


# -------------------------------------------------------------
# Abordagem 2: Resolução remota da árvore via JSON-RPC
# -------------------------------------------------------------
def resolver_no_servidor_jsonrpc(no_raiz):
    dados_arvore = Calculadora.para_dict(no_raiz)
    params = {"arvore": dados_arvore}
    return chamar_jsonrpc("calcular_arvore", params)


# -------------------------------------------------------------
# Interface do Menu
# -------------------------------------------------------------
def menu():
    print("=" * 55)
    print("       CALCULADORA DISTRIBUÍDA (JSON-RPC 2.0) - AT03")
    print("=" * 55)
    print("1. Calcular Expressão - Abordagem 1 (Decomposição Local)")
    print("2. Calcular Expressão - Abordagem 2 (Resolução Remota)")
    print("3. Operação Atómica Direta via JSON-RPC")
    print("4. Sair")
    print("=" * 55)


if __name__ == "__main__":
    while True:
        menu()
        opcao = input("Selecione uma opção (1-4): ").strip()

        if opcao == "4":
            print("A encerrar o cliente JSON-RPC...")
            break

        if opcao in ("1", "2"):
            expressao = input("\nDigite a expressão matemática (ex: ((10+2)*4)): ").strip()
            if not expressao:
                continue

            try:
                raiz = Calculadora.criar_arvore_expressao(expressao)

                if opcao == "1":
                    print("[*] A calcular via Abordagem 1 (requisições JSON-RPC atómicas)...")
                    resultado = resolver_no_cliente_jsonrpc(raiz)
                else:
                    print("[*] A calcular via Abordagem 2 (envio da árvore via JSON-RPC)...")
                    resultado = resolver_no_servidor_jsonrpc(raiz)

                print(f"\n=> Resultado: {resultado}\n")

            except Exception as erro:
                print(f"\n[!] Falha no JSON-RPC: {erro}\n")

        elif opcao == "3":
            try:
                op1 = float(input("Digite o primeiro número: "))
                operacao = input("Digite a operação (+, -, *, /, **): ").strip()
                op2 = float(input("Digite o segundo número: "))

                mapa_metodos = {'+': 'somar', '-': 'subtrair', '*': 'multiplicar', '/': 'dividir', '**': 'potencia'}
                metodo = mapa_metodos.get(operacao)
                if not metodo:
                    print("[!] Operação inválida.")
                    continue

                res = chamar_jsonrpc(metodo, {"op1": op1, "op2": op2})
                print(f"\n=> Resultado: {res}\n")

            except Exception as erro:
                print(f"\n[!] Falha no JSON-RPC: {erro}\n")

        else:
            print("Opção inválida, tente novamente.\n")