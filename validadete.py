from tabulate import tabulate
import termcolor
import json
import glob
from jsonschema import Draft7Validator  # Substitua Draft7Validator pela versão do esquema que você está usando

from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Definição dos esquemas
esquemas = {
    "basic": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "timeout": {"type": "integer"},
            "max_threads": {"type": "integer"},
            "auth_type": {"type": "string", "enum": ["basic"]},
            "credentials": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            }
        },
        "required": ["url", "timeout", "max_threads", "auth_type", "credentials"]
    },
    "digest": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "timeout": {"type": "integer"},
            "max_threads": {"type": "integer"},
            "auth_type": {"type": "string", "enum": ["digest"]},
            "credentials": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            }
        },
        "required": ["url", "timeout", "max_threads", "auth_type", "credentials"]
    },
    "bearer": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "timeout": {"type": "integer"},
            "max_threads": {"type": "integer"},
            "auth_type": {"type": "string", "enum": ["bearer"]},
            "credentials": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"}
                },
                "required": ["token"]
            }
        },
        "required": ["url", "timeout", "max_threads", "auth_type", "credentials"]
    },
    "form": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "timeout": {"type": "integer"},
            "max_threads": {"type": "integer"},
            "auth_type": {"type": "string", "enum": ["form"]},
            "login_url": {"type": "string", "format": "uri"},
            "form_data": {"type": "object"},
            "credentials": {"type": "object"}
        },
        "required": ["url", "timeout", "max_threads", "auth_type", "login_url", "form_data"]
    },
    
}
esquemas['onion_site'] = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "format": "uri",
            "pattern": "\\.onion$"
        },
        "depth": {"type": "integer", "minimum": 1},
        "max_threads": {"type": "integer", "minimum": 1},
        "timeout": {"type": "integer", "minimum": 1}
    },
    "required": ["url", "depth", "max_threads", "timeout"]
}
esquemas['url_normal'] = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "format": "uri",
            "pattern": "^https?://"  # Esta expressão regular assegura que a URL comece com http ou https
        },
        "timeout": {"type": "integer", "minimum": 1},
        "max_threads": {"type": "integer", "minimum": 1},
        "depth": {"type": "integer", "minimum": 1}
    },
    "required": ["url", "timeout", "max_threads", "depth"]
}


class ValidadorDeArquivosJSON:
    def __init__(self, esquemas):
        self.esquemas = esquemas
        self.resultados_globais = {"total": 0, "validos": 0, "invalidos": 0}
        self.detalhes_invalidos = {}

    def imprimir_mensagem(self, mensagem, cor="white"):
        print(termcolor.colored(mensagem, cor))

    def imprimir_detalhes_invalidos(self):
        if self.detalhes_invalidos:
            self.imprimir_mensagem("\nDetalhes dos Arquivos Inválidos:", "red")
            tabela = []
            for arquivo, detalhes in self.detalhes_invalidos.items():
                for detalhe in detalhes:
                    propriedade_faltante = self.extrair_propriedade_faltante(detalhe)
                    mensagem_correcao = f"Corrigir a propriedade '{propriedade_faltante}' conforme necessário."
                    tabela.append([arquivo, detalhe, mensagem_correcao])
            cabecalho = ['Caminho do Arquivo', 'Mensagem de Erro', 'Mensagem de Correção']
            self.imprimir_mensagem(tabulate(tabela, headers=cabecalho, tablefmt="grid"), "yellow")
        else:
            self.imprimir_mensagem("\nTodos os arquivos são válidos.", "green")


    def extrair_propriedade_faltante(self, mensagem_erro):
        if "' is a required property" in mensagem_erro:
            propriedade_faltante = mensagem_erro.split("'")[1]
            return propriedade_faltante
        else:
            return "Não especificado"


    def resumo_validacao(self):
        self.imprimir_mensagem("\nResumo da Validação:", "cyan")
        self.imprimir_mensagem(f"Total de arquivos processados: {self.resultados_globais['validos']-self.resultados_globais['invalidos']}", "cyan")
        self.imprimir_mensagem(f"Arquivos válidos: {self.resultados_globais['validos']}", "green")
        self.imprimir_mensagem(f"Arquivos inválidos: {self.resultados_globais['invalidos']}", "red")
        self.imprimir_detalhes_invalidos()


    def escolher_esquema_por_diretorio(self, diretorio):
        if "crawler_without_credential_web" in diretorio:
            return self.esquemas.get("url_normal")
        elif "crawler_with_credential_onion" in diretorio or "crawler_without_credential_onion" in diretorio:
            return self.esquemas.get("onion_site")
        else:
            return None

    def validar_documento_contra_esquema(self, documento, esquema):
        validator = Draft7Validator(esquema)
        erros = sorted(validator.iter_errors(documento), key=lambda e: e.path)
        if erros:
            detalhes_erros = []
            for erro in erros:
                detalhes_erro = erro.message
                if erro.path:
                    campo_faltante = ".".join([str(p) for p in erro.path])
                    detalhes_erro += f" Campo faltante ou inválido: {campo_faltante}."
                detalhes_erros.append(detalhes_erro)
            return False, detalhes_erros, [erro.path for erro in erros]
        return True, "Documento válido.", None

    def validar_arquivos_json(self, diretorios):
        for diretorio in diretorios:
            esquema = self.escolher_esquema_por_diretorio(diretorio)
            if not esquema:
                self.imprimir_mensagem(f"Esquema não encontrado para diretório: {diretorio}", "red")
                continue

            arquivos_json = glob.glob(f"{diretorio}/*.json")
            for arquivo in arquivos_json:
                with open(arquivo, 'r') as f:
                    try:
                        dados = json.load(f)
                        valido, mensagem, campo_faltante = self.validar_documento_contra_esquema(dados, esquema)
                        if valido:
                            self.resultados_globais["validos"] += 1
                        else:
                            self.resultados_globais["invalidos"] += 1
                            self.detalhes_invalidos[arquivo] = mensagem
                    except json.JSONDecodeError as e:
                        self.resultados_globais["invalidos"] += 1
                        self.detalhes_invalidos[arquivo] = f"Erro de decodificação JSON: {e}"
                    except Exception as e:
                        self.resultados_globais["invalidos"] += 1
                        self.detalhes_invalidos[arquivo] = f"Erro ao validar: {e}"

                self.resultados_globais["total"] += len(arquivos_json)

        self.resumo_validacao()
        return self.resultados_globais, self.detalhes_invalidos


lista_dir = ['crawler_without_credential_web', 'crawler_with_credential_onion', 'crawler_without_credential_onion']
validador = ValidadorDeArquivosJSON(esquemas)
validador.validar_arquivos_json(lista_dir)