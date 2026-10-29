import arvore


expressao = input("Digite a expressao matematica a ser calculada: ")
c1 = arvore.Calculadora
raiz = c1.criar_arvore_expressao(expressao)
# print(f"Operacao principal da raiz {raiz.operacao}")

resultado = c1.calcular_arvore(raiz)
print(f"Resultado final do cálculo: {resultado}")