

'''
import json
import os
from datetime import datetime

# Caminho para o JSON
CAMINHO_JSON = "acari-leis-2.json"

# Função para formatar data e hora
def agora_formatado():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

# Carrega o JSON
def carregar_dados_json(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

# Função para exibir as informações
def verificar_itens(dados):
    total = len(dados)
    for i, item in enumerate(dados, 1):
        print(f"\n=== Processando item {i} / {total} ===")
        print(f"{agora_formatado()} [INFO] Iniciando cadastro: {item.get('titulo', 'Sem título')}")
        print(f"{agora_formatado()} [INFO] Título: {item.get('titulo', 'Sem título')}")
        print(f"{agora_formatado()} [INFO] Data de Publicação: {item.get('data_publicacao', 'Sem data')}")
        print(f"{agora_formatado()} [INFO] Ementa: {item.get('ementa', 'Sem ementa')}")

        caminho_arquivo = item.get('arquivo', 'Sem arquivo')
        if os.path.exists(caminho_arquivo):
            print(f"{agora_formatado()} [INFO] Arquivo enviado: {caminho_arquivo}")
        else:
            print(f"{agora_formatado()} [ERRO] Arquivo não encontrado: {caminho_arquivo}")

# Execução principal
if __name__ == "__main__":
    try:
        dados = carregar_dados_json(CAMINHO_JSON)
        verificar_itens(dados)
    except Exception as e:
        print(f"{agora_formatado()} [ERRO] Falha ao processar o JSON: {e}")


'''


import json
import os

# Nome do arquivo JSON
CAMINHO_JSON = "acari-leis-6_ajustado.json"

# Lista de campos obrigatórios
CAMPOS_OBRIGATORIOS = ["Titulo", "Data", "Ementa", "Link PDF"]

def campo_preenchido(valor):
    return isinstance(valor, str) and valor.strip() != ""

def verificar_campos(dados):
    todos_ok = True
    for i, item in enumerate(dados, 1):
        erros = []
        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in item:
                erros.append(f"Campo ausente: '{campo}'")
            elif not campo_preenchido(item[campo]):
                erros.append(f"Campo vazio: '{campo}'")
        if erros:
            todos_ok = False
            print(f"\n[ERRO] Item {i} com problemas:")
            for erro in erros:
                print(f" - {erro}")
            print(" > Dados do item com problema:")
            print(json.dumps(item, indent=2, ensure_ascii=False))
    if todos_ok:
        print("\n✅ Todos os itens estão com os campos obrigatórios preenchidos.")

# Execução principal
if __name__ == "__main__":
    if not os.path.exists(CAMINHO_JSON):
        print(f"[ERRO] Arquivo JSON não encontrado: {CAMINHO_JSON}")
    else:
        try:
            with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
                dados = json.load(f)
            verificar_campos(dados)
        except Exception as e:
            print(f"[ERRO] Falha ao processar o JSON: {e}")

