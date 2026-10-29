"""  
Classe com árvore binária que segmenta a expressão matemática para que os cálculos possam ser efetuados.
"""

#importacoes de bibliotecas
import ast # biblioteca para representacao de arvore da espressao digitada

class Arvore:
    def __init__(self, operacao = None, left = None, right = None, valor = None):
        self.operacao = operacao # oepracoes +, -, *, /
        self.left = left         # subarvore a esquerda
        self.right = right       # subarvore a direita
        self.valor = valor       # números digitados
    


class Calculadora:
    # Funcao que percorre a arvore criada e transforma nos nós para a expressao
    @staticmethod
    def converte_express_arvore(no_ast):
        # se o nó for apenas um número
        if isinstance(no_ast, ast.Constant):
            return Arvore(valor=float(no_ast.value))
            
        # quando o nó for uma operacao binaria
        elif isinstance(no_ast, ast.BinOp):
            operadores = {
                ast.Add: '+',
                ast.Sub: '-',
                ast.Mult: '*',
                ast.Div: '/',
            }
            simbolo = operadores[type(no_ast.op)]
                
            # convertendo os lados direito e esquerdo
            filho_esquerdo = Calculadora.converte_express_arvore(no_ast.left)
            filho_direito = Calculadora.converte_express_arvore(no_ast.right)
                
            return Arvore(operacao=simbolo, left=filho_esquerdo, right=filho_direito)
        
    # le o texto digitado e retorna a arvore pronta
    def criar_arvore_expressao(texto_digitado):
        arvore_ast = ast.parse(texto_digitado, mode='eval')
        return Calculadora.converte_express_arvore(arvore_ast.body)
        

    def calcular_arvore(no):
        if no.valor is not None:
            return no.valor
        
        valor_esq = Calculadora.calcular_arvore(no.left)
        valor_dir = Calculadora.calcular_arvore(no.right)
        
        # aplicar a operacao no nó atual
        if no.operacao == '+':
            return valor_esq + valor_dir
        elif no.operacao == '-':
            return valor_esq - valor_dir
        elif no.operacao == '*':
            return valor_esq * valor_dir
        elif no.operacao == '/':
            if valor_dir == 0:
                raise ZeroDivisionError("Divisao por zero.")
            return valor_esq / valor_dir
        
    @staticmethod
    def para_dict(no):
        """Converte a Arvore em dict compatível com json."""
        if no is None:
            return None
        if no.valor is not None:
            return {"valor": no.valor}
        return {
            "operacao": no.operacao,
            "left": Calculadora.para_dict(no.left),
            "right": Calculadora.para_dict(no.right)
        }

    @staticmethod
    def de_dict(dados):
        """Reconstrói a Arvore a partir de um dict."""
        if dados is None:
            return None
        if "valor" in dados and dados["valor"] is not None:
            return Arvore(valor=float(dados["valor"]))
        return Arvore(
            operacao=dados.get("operacao"),
            left=Calculadora.de_dict(dados.get("left")),
            right=Calculadora.de_dict(dados.get("right"))
        )