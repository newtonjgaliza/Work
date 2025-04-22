import os
import json
import time
import logging
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException

#### ---- FUNÇÕES AUXILIARES ---- ####

def configurar_logging(pasta_nome):
    """Configura o logging dinâmico para cada pasta"""
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(f'log - {pasta_nome}.txt'),
            logging.StreamHandler()
        ]
    )

def registrar_erro_em_tempo_real(pasta_base, ano, nome_arquivo, arquivo_erros='arquivos-erro.txt'):
    """Registra um erro no arquivo em tempo real, organizado por pasta/ano."""
    cabecalho = f"#### {os.path.basename(pasta_base)} - {ano} ####"
    
    cabecalho_existente = False
    if os.path.exists(arquivo_erros):
        with open(arquivo_erros, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            cabecalho_existente = cabecalho in conteudo
    
    with open(arquivo_erros, 'a', encoding='utf-8') as f:
        if not cabecalho_existente:
            f.write(f"{cabecalho}\n")
        f.write(f"{nome_arquivo}\n")

def selecionar_categoria(navegador, nome_categoria):
    try:
        logging.info(f"Selecionando categoria: {nome_categoria}")
        categoria_select = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="form"]/div[1]/div[1]/select'))
        )
        select = Select(categoria_select)
        try:
            select.select_by_visible_text(nome_categoria)
            logging.info("Categoria selecionada pelo texto")
            return True
        except NoSuchElementException:
            options = [option.text for option in select.options]
            logging.warning(f"Categoria não encontrada! Opções disponíveis: {options}")
            return False
    except Exception as e:
        logging.error(f"Erro ao selecionar categoria: {str(e)}")
        return False

def gerar_titulo_do_arquivo(nome_arquivo):
    nome_base = os.path.basename(nome_arquivo)
    nome_sem_ext = nome_base.rsplit('.', 1)[0].strip()
    
    partes = nome_sem_ext.split(" - ", 1)
    if len(partes) == 2:
        titulo = partes[1].strip()
    else:
        indice_separador = nome_sem_ext.find("-") if "-" in nome_sem_ext else nome_sem_ext.find("_")
        if indice_separador != -1:
            titulo = nome_sem_ext[indice_separador + 1:].strip()
        else:
            logging.error(f"Nome do arquivo '{nome_arquivo}' não contém separador válido.")
            return None
    
    titulo = titulo.replace("-", " ").replace("_", " ")
    return titulo

def extrair_data_publicacao(nome_arquivo):
    try:
        nome_sem_ext = os.path.basename(nome_arquivo).rsplit('.', 1)[0].strip()
        partes = nome_sem_ext.split(" - ", 1)
        if len(partes) == 2:
            data_str = partes[0].strip()
        else:
            indice_separador = nome_sem_ext.find("-") if "-" in nome_sem_ext else nome_sem_ext.find("_")
            if indice_separador == -1:
                logging.error(f"Nome do arquivo '{nome_arquivo}' sem separador para data.")
                return None
            data_str = nome_sem_ext[:indice_separador].strip()
        
        if len(data_str) == 10 and data_str[4] == '-' and data_str[7] == '-':
            ano, mes, dia = data_str.split('-')
        else:
            data_str = data_str.replace("-", "/")
            partes_data = data_str.split("/")
            if len(partes_data) != 3:
                logging.error(f"Formato de data inválido em '{nome_arquivo}': {data_str}")
                return None
            dia, mes, ano = partes_data
        
        return f"{dia}/{mes}/{ano}"
    except Exception as e:
        logging.error(f"Erro ao extrair data de publicação do arquivo '{nome_arquivo}': {str(e)}")
        return None

#### ---- FUNÇÕES DE CADASTRO ---- ####

def cadastrar_categoria(navegador, nome_da_categoria):
    try:
        logging.info('Selecionando categoria')
        if not selecionar_categoria(navegador, nome_da_categoria):
            logging.error("Falha ao selecionar categoria")
            return False
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_categoria: {str(e)}")
        return False

def cadastrar_titulo(navegador, titulo):
    try:
        logging.info('Preenchendo título')
        campo_titulo = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section[2]/div/form/div[1]/div[2]/div[1]/div/input'))
        )
        campo_titulo.clear()
        campo_titulo.send_keys(titulo)
        
        WebDriverWait(navegador, 5).until(
            lambda d: campo_titulo.get_attribute('value').strip() == titulo.strip()
        )
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_titulo: {str(e)}")
        return False

def cadastrar_data(navegador, data_publicacao):
    try:
        if not data_publicacao:
            return True
            
        logging.info('Preenchendo data de publicação')
        campo_data = WebDriverWait(navegador, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="publication_date"]'))
        )
        campo_data.clear()
        campo_data.send_keys(data_publicacao)
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_data: {str(e)}")
        return False

def cadastrar_texto(navegador, texto):
    try:
        logging.info('Preenchendo texto principal')
        campo_texto = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.note-editable'))
        )
        campo_texto.clear()
        campo_texto.send_keys(texto)
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_texto: {str(e)}")
        return False

def adicionar_arquivo(nome_arquivo, navegador, caminho_pasta, titulo):
    try:
        logging.info("Clicando no botão 'Adicionar Arquivo'")
        navegador.find_element(By.ID, 'btn-adicionar').click()
        time.sleep(2)
        
        input_arquivo = navegador.find_element(By.CLASS_NAME, 'archives')
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        logging.info(f"Subindo o arquivo: {caminho_arquivo}")
        input_arquivo.send_keys(caminho_arquivo)

        campo_descricao = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.ID, 'description'))
        )
        campo_descricao.send_keys(titulo)

        WebDriverWait(navegador, 10).until(
            lambda d: campo_descricao.get_attribute('value').strip() != ''
        )
        
        time.sleep(5)
        logging.info(f"Arquivo {nome_arquivo} adicionado com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Erro ao adicionar o arquivo {nome_arquivo}: {str(e)}")
        navegador.save_screenshot(f'erro_arquivo_{nome_arquivo}.png')
        return False

def clicar_no_salvar(navegador):
    try:
        logging.info("Clicando no botão 'Salvar'")
        navegador.find_element(By.ID, 'btn-submit').click()
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.alert.alert-success'))
        )
        logging.info("Publicação salva com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Erro ao clicar no botão 'Salvar': {str(e)}")
        navegador.save_screenshot('erro_salvar.png')
        return False

def cadastrar_publicacao_com_upload(nome_arquivo, navegador, caminho_pasta, nome_da_categoria):
    try:
        titulo = gerar_titulo_do_arquivo(nome_arquivo)
        data_publicacao = extrair_data_publicacao(nome_arquivo)

        if not titulo or not data_publicacao:
            logging.warning(f"Arquivo {nome_arquivo} ignorado devido a erro na extração de título ou data.")
            return False

        titulo_truncado = titulo[:120] if len(titulo) > 120 else titulo
        if len(titulo) > 120:
            logging.warning(f"Título truncado (mais de 120 caracteres): {titulo}")

        logging.info('Acessando página de cadastro')
        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[1]/div[1]/a'))
        ).click()

        steps = [
            lambda: cadastrar_categoria(navegador, nome_da_categoria),
            lambda: cadastrar_titulo(navegador, titulo_truncado),
            lambda: cadastrar_data(navegador, data_publicacao),
            lambda: cadastrar_texto(navegador, titulo),
            lambda: adicionar_arquivo(nome_arquivo, navegador, caminho_pasta, titulo),
            lambda: clicar_no_salvar(navegador)
        ]

        for step in steps:
            if not step():
                logging.error("Interrompendo processo devido a erro em uma das etapas")
                return False

        time.sleep(2)
        return True

    except Exception as e:
        logging.error(f"Erro ao processar o documento {nome_arquivo}: {str(e)}")
        navegador.save_screenshot(f'erro_documento_{nome_arquivo}.png')
        return False

def reiniciar_navegador(config_cms):
    try:
        if 'navegador' in locals():
            navegador.quit()
        
        servico = Service(GeckoDriverManager().install())
        novo_navegador = webdriver.Firefox(service=servico)
        
        novo_navegador.get(config_cms['url'])
        novo_navegador.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys(config_cms['email'])
        novo_navegador.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(config_cms['password'])
        novo_navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()
        
        if config_cms['menu'] == 'Legislação':
            WebDriverWait(novo_navegador, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-balance-scale'))
            ).click()
        elif config_cms['menu'] == 'Publicações':
            WebDriverWait(novo_navegador, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-book'))
            ).click()
            
        return novo_navegador
        
    except Exception as e:
        logging.error(f"Falha ao reiniciar navegador: {str(e)}")
        return None

#### ---- FUNÇÕES DE PROCESSAMENTO ---- ####

def mover_para_pasta(nome_arquivo, origem, destino):
    try:
        ano = os.path.basename(origem)
        destino_final = os.path.join(destino, ano)
        os.makedirs(destino_final, exist_ok=True)
        
        shutil.move(
            os.path.join(origem, nome_arquivo),
            os.path.join(destino_final, nome_arquivo)
        )
        logging.info(f"Arquivo movido para {destino_final}")
    except Exception as e:
        logging.error(f"Falha ao mover arquivo: {str(e)}")

def processar_arquivos(lista_de_arquivos, config_cms, caminho_pasta, nome_categoria, caminho_backup, caminho_erros):
    total = len(lista_de_arquivos)
    erros = []
    navegador = None

    for i, nome_arquivo in enumerate(lista_de_arquivos, 1):
        try:
            if navegador is None:
                navegador = reiniciar_navegador(config_cms)
                if not navegador:
                    raise Exception("Não foi possível reiniciar o navegador")

            logging.info(f"\n{'='*30}")
            logging.info(f"Processando {i}/{total}: {nome_arquivo}")
            
            sucesso = cadastrar_publicacao_com_upload(nome_arquivo, navegador, caminho_pasta, nome_categoria)
            
            if sucesso:
                mover_para_pasta(nome_arquivo, caminho_pasta, caminho_backup)
            else:
                raise Exception("Falha no cadastro")

        except Exception as e:
            logging.error(f"Erro grave no processamento: {str(e)}")
            erros.append(nome_arquivo)
            
            mover_para_pasta(nome_arquivo, caminho_pasta, caminho_erros)
            
            if navegador:
                navegador.quit()
                navegador = None
                
            navegador = reiniciar_navegador(config_cms)
            if not navegador:
                break

    if navegador:
        navegador.quit()
    return erros

def processar_pastas(pasta_base, config_cms, nome_da_categoria, caminho_backup, caminho_erros):
    erros_por_ano = {}
    try:
        pastas_anos = [f for f in os.listdir(pasta_base) 
                      if os.path.isdir(os.path.join(pasta_base, f)) 
                      and f.isdigit() 
                      and 1970 <= int(f) <= 2025]
        
        pastas_anos = sorted(pastas_anos, key=lambda x: int(x), reverse=True)
        logging.info(f"Pastas encontradas para processamento: {pastas_anos}")

    except Exception as e:
        logging.error(f"Erro ao listar pastas: {str(e)}")
        return erros_por_ano

    for pasta_ano in pastas_anos:
        caminho_pasta = os.path.join(pasta_base, pasta_ano)
        logging.info(f"\n{'='*50}")
        logging.info(f"Processando ano: {pasta_ano}")
        logging.info(f"Caminho: {caminho_pasta}")
        logging.info(f"{'='*50}\n")

        if not os.path.exists(caminho_pasta):
            logging.error(f"Pasta {caminho_pasta} não encontrada!")
            continue

        try:
            arquivos = [f for f in os.listdir(caminho_pasta) 
                       if f.lower().endswith(('.pdf', '.doc', '.docx'))]
            
            if not arquivos:
                logging.warning(f"Nenhum arquivo encontrado em {pasta_ano}")
                continue
                
            logging.info(f"Arquivos encontrados em {pasta_ano}: {len(arquivos)}")
            erros = processar_arquivos(arquivos, config_cms, caminho_pasta, nome_da_categoria, caminho_backup, caminho_erros)
            if erros:
                erros_por_ano[pasta_ano] = erros

        except Exception as e:
            logging.error(f"Erro ao processar {pasta_ano}: {str(e)}")
            continue

    return erros_por_ano

def escrever_arquivo_erros(erros_global):
    with open('arquivos-erro-consolidado.txt', 'w', encoding='utf-8') as f:
        for (pasta_base, ano), arquivos in erros_global.items():
            f.write(f"#### {pasta_base} - {ano} ####\n")
            for arquivo in arquivos:
                f.write(f"{arquivo}\n")
            f.write("\n")

#### ---- EXECUÇÃO PRINCIPAL ---- ####
if __name__ == "__main__":
    erros_global = {}
    try:
        with open('config-v3.json', 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            
        upload_config = config['configuracoes'][0]['upload']
        cms_config = config['configuracoes'][0]['cms']
        
        pasta_nome = os.path.basename(upload_config['caminho_base'])
        configurar_logging(pasta_nome)
        
        logging.info(f'\n{"#"*50}')
        logging.info(f'INICIANDO PROCESSAMENTO PARA: {pasta_nome}')
        logging.info(f'Categoria: {upload_config["nome_da_categoria"]}')
        logging.info(f'Menu CMS: {upload_config["menu_do_cms"]}')
        logging.info(f'{"#"*50}\n')

        Path(upload_config['caminho_backup']).mkdir(parents=True, exist_ok=True)
        Path(upload_config['caminho_erros']).mkdir(parents=True, exist_ok=True)

        erros = processar_pastas(
            pasta_base=upload_config['caminho_base'],
            config_cms={
                'url': cms_config['url'],
                'email': cms_config['email'],
                'password': cms_config['password'],
                'menu': upload_config['menu_do_cms']
            },
            nome_da_categoria=upload_config['nome_da_categoria'],
            caminho_backup=upload_config['caminho_backup'],
            caminho_erros=upload_config['caminho_erros']
        )
        
        if erros:
            escrever_arquivo_erros(erros)
            logging.error("Alguns arquivos não foram processados. Verifique a pasta de erros.")
        else:
            logging.info("Todos os arquivos processados com sucesso!")

    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
