import os
import json
import img2pdf
import logging
from datetime import datetime

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'log-conversao-pdf-{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'),
            logging.StreamHandler()
        ]
    )
    logging.info("Sistema de log inicializado")

def carregar_configuracoes():
    try:
        with open('config.json', 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            logging.info("Configurações carregadas com sucesso")
            return config.get('configuracoes', [])
    except Exception as e:
        logging.error(f"Erro ao carregar configurações: {str(e)}")
        return []

def converter_para_pdf(caminho_imagem, caminho_pdf):
    try:
        with open(caminho_pdf, "wb") as arquivo_pdf:
            arquivo_pdf.write(img2pdf.convert(caminho_imagem))
        logging.info(f"Conversão bem-sucedida: {os.path.basename(caminho_imagem)} -> {os.path.basename(caminho_pdf)}")
        return True
    except Exception as e:
        logging.error(f"Falha na conversão de {os.path.basename(caminho_imagem)}: {str(e)}")
        return False

def remover_arquivos_redundantes(caminho_pdf):
    extensoes_para_remover = ['.png', '.jpg', '.jpeg']
    base_name = os.path.splitext(caminho_pdf)[0]
    removidos = 0

    for ext in extensoes_para_remover:
        caminho_arquivo = base_name + ext
        if os.path.exists(caminho_arquivo) and caminho_arquivo != caminho_pdf:
            try:
                os.remove(caminho_arquivo)
                logging.info(f"Arquivo removido: {os.path.basename(caminho_arquivo)}")
                removidos += 1
            except Exception as e:
                logging.error(f"Erro ao remover {os.path.basename(caminho_arquivo)}: {str(e)}")
    
    return removidos

def processar_diretorio(diretorio_base):
    metricas = {
        'verificados': 0,
        'convertidos': 0,
        'ignorados': 0,
        'removidos': 0,
        'erros': 0
    }

    logging.info(f"\n{'=' * 60}")
    logging.info(f"INICIANDO PROCESSAMENTO: {diretorio_base}")
    logging.info(f"{'=' * 60}")

    try:
        for raiz, _, arquivos in os.walk(diretorio_base):
            for arquivo in arquivos:
                metricas['verificados'] += 1
                nome_base, extensao = os.path.splitext(arquivo)
                extensao = extensao.lower()

                if extensao in ['.jpg', '.jpeg', '.png']:
                    caminho_original = os.path.join(raiz, arquivo)
                    caminho_pdf = os.path.join(raiz, nome_base + ".pdf")

                    if os.path.exists(caminho_pdf):
                        metricas['ignorados'] += 1
                        logging.warning(f"PDF já existe: {nome_base}.pdf")
                        continue

                    if converter_para_pdf(caminho_original, caminho_pdf):
                        metricas['convertidos'] += 1
                        metricas['removidos'] += remover_arquivos_redundantes(caminho_pdf)
                    else:
                        metricas['erros'] += 1

    except Exception as e:
        logging.critical(f"ERRO NO PROCESSAMENTO: {str(e)}")
        metricas['erros'] += 1

    logging.info(f"\nRESUMO PARA {diretorio_base}:")
    logging.info(f"Arquivos verificados: {metricas['verificados']}")
    logging.info(f"Conversões realizadas: {metricas['convertidos']}")
    logging.info(f"Arquivos ignorados: {metricas['ignorados']}")
    logging.info(f"Arquivos removidos: {metricas['removidos']}")
    logging.info(f"Erros encontrados: {metricas['erros']}")
    logging.info(f"{'=' * 60}\n")

    return metricas

def gerar_relatorio_consolidado(resultados):
    logging.info("\n" + "=" * 60)
    logging.info("RELATÓRIO CONSOLIDADO".center(60))
    logging.info("=" * 60)
    
    totais = {
        'verificados': sum(r['verificados'] for r in resultados),
        'convertidos': sum(r['convertidos'] for r in resultados),
        'ignorados': sum(r['ignorados'] for r in resultados),
        'removidos': sum(r['removidos'] for r in resultados),
        'erros': sum(r['erros'] for r in resultados)
    }

    logging.info(f"TOTAL DE ARQUIVOS VERIFICADOS: {totais['verificados']}")
    logging.info(f"TOTAL DE CONVERSÕES: {totais['convertidos']}")
    logging.info(f"TOTAL DE ARQUIVOS IGNORADOS: {totais['ignorados']}")
    logging.info(f"TOTAL DE ARQUIVOS REMOVIDOS: {totais['removidos']}")
    logging.info(f"TOTAL DE ERROS: {totais['erros']}")
    logging.info("=" * 60)

def executar_processamento():
    configurar_logging()
    configuracoes = carregar_configuracoes()
    
    if not configuracoes:
        logging.error("Nenhuma configuração válida encontrada. Verifique o arquivo config.json")
        return

    resultados = []
    for config in configuracoes:
        caminho_base = config.get('upload', {}).get('caminho_base')
        if not caminho_base:
            logging.error("Configuração inválida: 'upload.caminho_base' não encontrado")
            continue
        if not os.path.exists(caminho_base):
            logging.error(f"Diretório não encontrado: {caminho_base}")
            continue
        resultados.append(processar_diretorio(caminho_base))

    gerar_relatorio_consolidado(resultados)
    logging.info("\nPROCESSO CONCLUÍDO COM SUCESSO")

if __name__ == "__main__":
    executar_processamento()
