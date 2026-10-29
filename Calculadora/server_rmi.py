"""
Servidor RMI utilizando Pyro5.
Regista o objeto remoto CalculadoraRMI para invocação remota de métodos.
"""

import Pyro5.api
from arvore import Calculadora


@Pyro5.api.expose
class CalculadoraRMI:
    def somar(self, op1, op2):
        return float(op1) + float(op2)

    def subtrair(self, op1, op2):
        return float(op1) - float(op2)

    def multiplicar(self, op1, op2):
        return float(op1) * float(op2)

    def dividir(self, op1, op2):
        if float(op2) == 0:
            raise ZeroDivisionError("Divisao por zero.")
        return float(op1) / float(op2)

    def calcular_expressao(self, dados_arvore):
        """
        Recebe a árvore serializada em dict e calcula recursivamente no servidor.
        """
        arvore_obj = Calculadora.de_dict(dados_arvore)
        return Calculadora.calcular_arvore(arvore_obj)


def iniciar_servidor(host="192.168.5.165", porta=9090):
    # Cria o daemon do Pyro associado ao IP e porta pretendidos
    daemon = Pyro5.api.Daemon(host=host, port=porta)
    
    # Regista o objeto com um identificador fixo para facilitar a ligação do cliente
    uri = daemon.register(CalculadoraRMI, objectId="calculadora_rmi")
    
    print("=" * 60)
    print("           SERVIDOR RMI (PYRO5) EM EXECUÇÃO")
    print("=" * 60)
    print(f"Objeto remoto pronto no URI:\n{uri}")
    print("=" * 60)
    print("A aguardar chamadas remotas de métodos...")
    
    daemon.requestLoop()


if __name__ == "__main__":
    iniciar_servidor()