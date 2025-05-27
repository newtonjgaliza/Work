import json
import os
import re
from datetime import datetime
from unicodedata import normalize

# Nome do arquivo de entrada
CAMINHO_JSON = "acari-leis-6.json"

# Função para formatar data e hora
def agora_formatado():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

# Função para remover acentos dos nomes dos meses
def remover_acentos(txt):
    return normalize('NFD', txt).encode('ascii', 'ignore').decode('utf-8')

# Mapeamento dos meses
MESES = {
    "janeiro": "01", "fevereiro": "02", "marco": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
    "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
}

# Função para tentar extrair a data do campo "Titulo"
def extrair_data_do_titulo(titulo):
    regex = r"(\d{1,2}) de (\w+) de (\d{4})"
    match = re.search(regex, titulo, flags=re.IGNORECASE)
    if match:
        dia, mes_nome, ano = match.groups()
        mes_nome_normalizado = remover_acentos(mes_nome.lower())
        mes = MESES.get(mes_nome_normalizado)
        if mes:
            return f"{int(dia):02d}/{mes}/{ano}"
    return None

# Carrega e corrige os dados
def corrigir_dados(caminho_entrada):
    with open(caminho_entrada, "r", encoding="utf-8") as f:
        dados = json.load(f)

    total_corrigidos = 0

    for item in dados:
        if "Data" not in item or not item["Data"].strip():
            titulo = item.get("Titulo", "")
            data_extraida = extrair_data_do_titulo(titulo)
            if data_extraida:
                item["Data"] = data_extraida
                total_corrigidos += 1
                print(f"{agora_formatado()} [INFO] Data corrigida para: {titulo} -> {data_extraida}")
            else:
                print(f"{agora_formatado()} [AVISO] Não foi possível extrair data do título: {titulo}")

    return dados, total_corrigidos

# Salva o novo JSON com sufixo "_ajustado"
def salvar_json_ajustado(caminho_original, dados_corrigidos):
    nome_base, ext = os.path.splitext(caminho_original)
    novo_caminho = f"{nome_base}_ajustado{ext}"
    with open(novo_caminho, "w", encoding="utf-8") as f:
        json.dump(dados_corrigidos, f, ensure_ascii=False, indent=2)
    return novo_caminho

# Execução principal
if __name__ == "__main__":
    if not os.path.exists(CAMINHO_JSON):
        print(f"[ERRO] Arquivo JSON não encontrado: {CAMINHO_JSON}")
    else:
        try:
            dados_corrigidos, total = corrigir_dados(CAMINHO_JSON)
            novo_arquivo = salvar_json_ajustado(CAMINHO_JSON, dados_corrigidos)
            print(f"\n✅ Total de itens corrigidos: {total}")
            print(f"📁 Novo arquivo salvo em: {novo_arquivo}")
        except Exception as e:
            print(f"[ERRO] Falha ao processar o JSON: {e}")


