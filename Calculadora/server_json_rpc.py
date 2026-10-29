"""
Servidor JSON-RPC 2.0 para a Calculadora Distribuída (AT03).
Implementa o protocolo padrão com validação de payload, dispatch de métodos e envelopes com id.
"""

import socket
import json
from arvore import Calculadora


def executar_metodo(metodo, params):
    """Encaminha o método requisitado para a função correspondente."""
    if metodo == "somar":
        return float(params["op1"]) + float(params["op2"])
    elif metodo == "subtrair":
        return float(params["op1"]) - float(params["op2"])
    elif metodo == "multiplicar":
        return float(params["op1"]) * float(params["op2"])
    elif metodo == "dividir":
        if float(params["op2"]) == 0:
            raise ZeroDivisionError("Divisão por zero.")
        return float(params["op1"]) / float(params["op2"])
    elif metodo == "calcular_arvore":
        arvore_reconstruida = Calculadora.de_dict(params["arvore"])
        return Calculadora.calcular_arvore(arvore_reconstruida)
    else:
        raise ValueError(f"Método não encontrado: {metodo}")


def processar_requisicao_jsonrpc(dados_brutos):
    """Interpreta e processa a mensagem de acordo com a especificação JSON-RPC 2.0."""
    try:
        req = json.loads(dados_brutos)
    except json.JSONDecodeError:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error (JSON inválido)"},
            "id": None
        }

    # Validação do envelope JSON-RPC 2.0
    if req.get("jsonrpc") != "2.0" or "method" not in req:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "Invalid Request (formato JSON-RPC 2.0 inválido)"},
            "id": req.get("id")
        }

    req_id = req.get("id")
    metodo = req.get("method")
    params = req.get("params", {})

    try:
        resultado = executar_metodo(metodo, params)
        return {
            "jsonrpc": "2.0",
            "result": resultado,
            "id": req_id
        }
    except ZeroDivisionError as zde:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(zde)},
            "id": req_id
        }
    except ValueError as ve:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": str(ve)},
            "id": req_id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            "id": req_id
        }


def iniciar_servidor(host="0.0.0.0", porta=9094):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((host, porta))
    servidor.listen(5)

    print("=" * 60)
    print(f"[*] Servidor JSON-RPC 2.0 em execução em {host}:{porta}...")
    print("=" * 60)

    while True:
        cliente, _ = servidor.accept()
        try:
            dados = cliente.recv(4096).decode("utf-8")
            if dados:
                resposta = processar_requisicao_jsonrpc(dados)
                cliente.sendall(json.dumps(resposta).encode("utf-8"))
        finally:
            cliente.close()


if __name__ == "__main__":
    iniciar_servidor()