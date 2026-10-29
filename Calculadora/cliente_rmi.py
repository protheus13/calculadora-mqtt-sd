"""
Cliente RMI utilizando Pyro5.
Liga-se ao objeto remoto CalculadoraRMI através do URI configurado.
Suporta as duas abordagens da AT03:
1. Decomposição local da árvore com chamadas remotas atómicas.
2. Envio da estrutura em dicionário para resolução completa remota.
"""

import Pyro5.api
from arvore import Calculadora


# URI correspondente ao objeto registado no server_rmi.py
HOST_SERVIDOR = "192.168.5.165"
PORTA_SERVIDOR = 9090
URI_CALCULADORA = f"PYRO:calculadora_rmi@{HOST_SERVIDOR}:{PORTA_SERVIDOR}"


def obter_proxy():
    """Cria e retorna uma referência remota (Proxy) para o objeto no servidor."""
    return Pyro5.api.Proxy(URI_CALCULADORA)


# -------------------------------------------------------------
# Abordagem 1: Decomposição no Cliente com invocações RMI atómicas
# -------------------------------------------------------------
def resolver_no_cliente_via_rmi(no, proxy):
    """
    Percorre a árvore recursivamente no cliente.
    Invoca o método remoto adequado (somar, subtrair, etc.) para cada nó de operação.
    """
    # Caso base: nó folha com valor numérico
    if no.valor is not None:
        return no.valor

    # Resolve os ramos esquerdo e direito recursivamente
    valor_esq = resolver_no_cliente_via_rmi(no.left, proxy)
    valor_dir = resolver_no_cliente_via_rmi(no.right, proxy)

    # Invocação remota de método diretamente pelo proxy RMI
    if no.operacao == '+':
        return proxy.somar(valor_esq, valor_dir)
    elif no.operacao == '-':
        return proxy.subtrair(valor_esq, valor_dir)
    elif no.operacao == '*':
        return proxy.multiplicar(valor_esq, valor_dir)
    elif no.operacao == '/':
        return proxy.dividir(valor_esq, valor_dir)
    else:
        raise ValueError(f"Operação desconhecida: {no.operacao}")


# -------------------------------------------------------------
# Abordagem 2: Resolução remota com passagem da árvore serializada
# -------------------------------------------------------------
def resolver_no_servidor_arvore_completa(no_raiz, proxy):
    """
    Serializa a árvore de nós num dicionário e passa para o método
    remoto 'calcular_expressao' resolver integralmente no servidor.
    """
    dados_arvore = Calculadora.para_dict(no_raiz)
    return proxy.calcular_expressao(dados_arvore)


# -------------------------------------------------------------
# Interface do Cliente
# -------------------------------------------------------------
def menu():
    print("=" * 55)
    print("      CALCULADORA DISTRIBUÍDA (RMI / PYRO5) - AT03")
    print("=" * 55)
    print("1. Calcular Expressão - Abordagem 1 (Decomposição Local)")
    print("2. Calcular Expressão - Abordagem 2 (Resolução Remota)")
    print("3. Operação Atómica Direta via RMI")
    print("4. Sair")
    print("=" * 55)


if __name__ == "__main__":
    # Inicializa o proxy remoto
    proxy_calc = obter_proxy()

    while True:
        menu()
        opcao = input("Selecione uma opção (1-4): ").strip()

        if opcao == "4":
            print("A encerrar o cliente RMI...")
            break

        if opcao in ("1", "2"):
            expressao = input("\nDigite a expressão matemática (ex: ((10+2)*4)): ").strip()
            if not expressao:
                continue

            try:
                # Constrói a árvore de expressão localmente
                raiz = Calculadora.criar_arvore_expressao(expressao)

                if opcao == "1":
                    print("[*] A calcular via Abordagem 1 (múltiplas invocações RMI)...")
                    resultado = resolver_no_cliente_via_rmi(raiz, proxy_calc)
                else:
                    print("[*] A calcular via Abordagem 2 (invocação remota da árvore)...")
                    resultado = resolver_no_servidor_arvore_completa(raiz, proxy_calc)

                print(f"\n=> Resultado: {resultado}\n")

            except Exception as erro:
                print(f"\n[!] Falha na invocação RMI: {erro}\n")

        elif opcao == "3":
            try:
                op1 = float(input("Digite o primeiro número: "))
                operacao = input("Digite a operação (+, -, *, /): ").strip()
                op2 = float(input("Digite o segundo número: "))

                if operacao == '+':
                    resultado = proxy_calc.somar(op1, op2)
                elif operacao == '-':
                    resultado = proxy_calc.subtrair(op1, op2)
                elif operacao == '*':
                    resultado = proxy_calc.multiplicar(op1, op2)
                elif operacao == '/':
                    resultado = proxy_calc.dividir(op1, op2)
                else:
                    print("[!] Operação inválida.")
                    continue

                print(f"\n=> Resultado: {resultado}\n")

            except Exception as erro:
                print(f"\n[!] Falha na invocação RMI: {erro}\n")

        else:
            print("Opção inválida, tente novamente.\n")