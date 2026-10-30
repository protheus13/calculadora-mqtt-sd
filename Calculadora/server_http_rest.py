"""
Servidor HTTP-REST para a Calculadora Distribuída (AT03 - Questão 4).
Utiliza a biblioteca nativa http.server do Python para processar endpoints REST em JSON.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from arvore import Calculadora


class CalculadoraRestHandler(BaseHTTPRequestHandler):
    def _responder_json(self, codigo_status, corpo_dict):
        """Envia cabeçalhos HTTP e o payload serializado em JSON."""
        corpo_bytes = json.dumps(corpo_dict).encode("utf-8")
        self.send_response(codigo_status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo_bytes)))
        self.end_headers()
        self.wfile.write(corpo_bytes)

    def do_POST(self):
        """Processa requisições REST via POST."""
        tamanho_conteudo = int(self.headers.get("Content-Length", 0))
        dados_brutos = self.rfile.read(tamanho_conteudo).decode("utf-8")

        try:
            dados = json.loads(dados_brutos) if dados_brutos else {}
        except json.JSONDecodeError:
            self._responder_json(400, {"erro": "Corpo da requisição não é um JSON válido."})
            return

        # Rota 1: Operações básicas atómicas (/operacao)
        if self.path == "/operacao":
            operacao = dados.get("operacao")
            try:
                op1 = float(dados.get("op1"))
                op2 = float(dados.get("op2"))

                if operacao == '+':
                    resultado = op1 + op2
                elif operacao == '-':
                    resultado = op1 - op2
                elif operacao == '*':
                    resultado = op1 * op2
                elif operacao == '/':
                    if op2 == 0:
                        self._responder_json(400, {"erro": "Divisão por zero."})
                        return
                    resultado = op1 / op2
                elif operacao == '**':
                    resultado = op1 ** op2
                else:
                    self._responder_json(400, {"erro": f"Operação desconhecida: {operacao}"})
                    return

                self._responder_json(200, {"resultado": resultado})

            except (TypeError, ValueError) as e:
                self._responder_json(400, {"erro": f"Parâmetros numéricos inválidos: {str(e)}"})

        # Rota 2: Avaliação da árvore de expressão (/calcular_arvore)
        elif self.path == "/calcular_arvore":
            dados_arvore = dados.get("arvore")
            if not dados_arvore:
                self._responder_json(400, {"erro": "Chave 'arvore' ausente na requisição."})
                return

            try:
                arvore_obj = Calculadora.de_dict(dados_arvore)
                resultado = Calculadora.calcular_arvore(arvore_obj)
                self._responder_json(200, {"resultado": resultado})
            except ZeroDivisionError:
                self._responder_json(400, {"erro": "Divisão por zero ao avaliar a árvore."})
            except Exception as e:
                self._responder_json(500, {"erro": f"Erro interno ao calcular árvore: {str(e)}"})

        else:
            self._responder_json(404, {"erro": "Endpoint não encontrado."})

    def log_message(self, format, *args):
        """Silencia logs verbosos no terminal para manter a consola limpa."""
        print(f"[REST Log] {self.address_string()} - {format % args}")


def iniciar_servidor(host="0.0.0.0", porta=8080):
    servidor_http = HTTPServer((host, porta), CalculadoraRestHandler)
    print("=" * 60)
    print(f"[*] Servidor HTTP-REST em execução em http://{host}:{porta}...")
    print("=" * 60)
    try:
        servidor_http.serve_forever()
    except KeyboardInterrupt:
        print("\nA encerrar o servidor HTTP-REST...")
        servidor_http.server_close()


if __name__ == "__main__":
    iniciar_servidor()