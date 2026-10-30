"""
Cliente HTTP-REST para a Calculadora Distribuída (AT03 - Questão 4).
Implementa política de RETRY com temporizador para tolerância a falhas transitórias.
"""

import urllib.request
import urllib.error
import json
import time
from arvore import Calculadora


URL_BASE = "http://192.168.5.165:8080"

# Parâmetros da Política de Retry exigida na AT03
MAX_RETRIES = 3
TEMPO_ESPERA_SEGUNDOS = 2.0


def enviar_requisicao_rest_com_retry(endpoint, payload_dict):
    """
    Executa um pedido POST HTTP para o endpoint especificado.
    Caso ocorra falha de ligação ou timeout, aplica política de Retry.
    """
    url = f"{URL_BASE}{endpoint}"
    corpo_bytes = json.dumps(payload_dict).encode("utf-8")

    tentativa = 1
    while tentativa <= MAX_RETRIES:
        try:
            req = urllib.request.Request(
                url,
                data=corpo_bytes,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=5) as resposta:
                dados_resposta = resposta.read().decode("utf-8")
                return json.loads(dados_resposta)

        except urllib.error.HTTPError as he:
            # Erros 4xx/5xx devolvidos pelo servidor HTTP
            detalhe = he.read().decode("utf-8")
            try:
                erro_json = json.loads(detalhe)
                mensagem_erro = erro_json.get("erro", detalhe)
            except Exception:
                mensagem_erro = detalhe
            raise RuntimeError(f"Erro HTTP {he.code}: {mensagem_erro}")

        except (urllib.error.URLError, TimeoutError) as conexao_erro:
            # Servidor indisponível ou timeout de rede: aciona o RETRY
            print(f"[!] Tentativa {tentativa}/{MAX_RETRIES} falhou ({conexao_erro.reason if hasattr(conexao_erro, 'reason') else conexao_erro}).")
            if tentativa < MAX_RETRIES:
                print(f"[*] A aguardar {TEMPO_ESPERA_SEGUNDOS}s antes da próxima tentativa...")
                time.sleep(TEMPO_ESPERA_SEGUNDOS)
                tentativa += 1
            else:
                raise ConnectionError(f"Falha de conexão com o servidor REST após {MAX_RETRIES} tentativas.")


# -------------------------------------------------------------
# Abordagem 1: Decomposição local com requisições REST atómicas
# -------------------------------------------------------------
def resolver_no_cliente_rest(no):
    if no.valor is not None:
        return no.valor

    val_esq = resolver_no_cliente_rest(no.left)
    val_dir = resolver_no_cliente_rest(no.right)

    payload = {
        "operacao": no.operacao,
        "op1": val_esq,
        "op2": val_dir
    }

    resposta = enviar_requisicao_rest_com_retry("/operacao", payload)
    return resposta.get("resultado")


# -------------------------------------------------------------
# Abordagem 2: Envio da árvore serializada para resolução REST
# -------------------------------------------------------------
def resolver_no_servidor_rest(no_raiz):
    dados_arvore = Calculadora.para_dict(no_raiz)
    payload = {"arvore": dados_arvore}

    resposta = enviar_requisicao_rest_com_retry("/calcular_arvore", payload)
    return resposta.get("resultado")


# -------------------------------------------------------------
# Interface do Cliente
# -------------------------------------------------------------
def menu():
    print("=" * 55)
    print("       CALCULADORA DISTRIBUÍDA (HTTP-REST) - AT03")
    print("=" * 55)
    print("1. Calcular Expressão - Abordagem 1 (Decomposição Local)")
    print("2. Calcular Expressão - Abordagem 2 (Resolução Remota)")
    print("3. Operação Atómica Direta via REST")
    print("4. Sair")
    print("=" * 55)


if __name__ == "__main__":
    while True:
        menu()
        opcao = input("Selecione uma opção (1-4): ").strip()

        if opcao == "4":
            print("A encerrar o cliente REST...")
            break

        if opcao in ("1", "2"):
            expressao = input("\nDigite a expressão matemática (ex: ((10+2)*4)): ").strip()
            if not expressao:
                continue

            try:
                raiz = Calculadora.criar_arvore_expressao(expressao)

                if opcao == "1":
                    print("[*] A calcular via Abordagem 1 (múltiplos pedidos POST REST)...")
                    resultado = resolver_no_cliente_rest(raiz)
                else:
                    print("[*] A calcular via Abordagem 2 (POST da árvore completa)...")
                    resultado = resolver_no_servidor_rest(raiz)

                print(f"\n=> Resultado: {resultado}\n")

            except Exception as erro:
                print(f"\n[!] Falha no processamento REST: {erro}\n")

        elif opcao == "3":
            try:
                op1 = float(input("Digite o primeiro número: "))
                operacao = input("Digite a operação (+, -, *, /, **): ").strip()
                op2 = float(input("Digite o segundo número: "))

                payload = {"operacao": operacao, "op1": op1, "op2": op2}
                resp = enviar_requisicao_rest_com_retry("/operacao", payload)
                print(f"\n=> Resultado: {resp.get('resultado')}\n")

            except Exception as erro:
                print(f"\n[!] Falha no processamento REST: {erro}\n")

        else:
            print("Opção inválida, tente novamente.\n")