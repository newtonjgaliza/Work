1import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Variáveis globais
LOG_PATH = "log_processamento.txt"
falhas = []

def log(msg, erro=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {'[ERRO]' if erro else '[INFO]'} {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def login_cms(navegador, config):
    navegador.get(config['cms_url'])
    WebDriverWait(navegador, 5).until(EC.presence_of_element_located((By.NAME, 'email')))
    navegador.find_element(By.NAME, 'email').send_keys(config['cms_email'])
    navegador.find_element(By.NAME, 'password').send_keys(config['cms_password'])
    navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

def cadastrar_item(item, navegador, config):
    menu_opcao = config.get('menu_opcao', 'Legislação')

    # Clicar na opção do menu conforme o config
    WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, menu_opcao))
    ).click()

    WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.LINK_TEXT, 'Cadastrar Legislação'))
    ).click()

    categoria_select = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.NAME, 'category_contents_id'))
    )
    Select(categoria_select).select_by_visible_text(config['categoria_legislacao'])

    titulo_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.NAME, 'title'))
    )
    titulo_input.clear()
    titulo_input.send_keys(item['Titulo'])
    log(f"Título: {item['Titulo']}")

    data_formatada = item.get('Data', '')
    data_input = navegador.find_element(By.ID, 'publication_date')
    data_input.clear()
    data_input.send_keys(data_formatada)
    log(f"Data de Publicação: {data_formatada}")

    campo_texto = navegador.find_element(By.CSS_SELECTOR, 'div.note-editable')
    campo_texto.send_keys(item['Ementa'])
    log(f"Ementa: {item['Ementa']}")

    botao_adicionar = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.ID, 'btn-adicionar'))
    )
    botao_adicionar.click()

    campo_arquivo = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[type="file"][name="archive[][]"][class="archives form-control mb-2"]')
        )
    )

    caminho_absoluto = os.path.abspath(item['Arquivo'])
    campo_arquivo.send_keys(caminho_absoluto)
    log(f"Arquivo enviado: {caminho_absoluto}")

    descricao_input = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.NAME, 'archive[][description]'))
    )
    descricao_input.send_keys(item['Titulo'])

    botao_salvar = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.ID, 'btn-submit'))
    )
    botao_salvar.click()

    time.sleep(2)

# --- MAIN ---
if __name__ == "__main__":
    try:
        with open("config.json", "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        log("Arquivo config.json não encontrado.", erro=True)
        exit(1)

    json_path = config.get("json_dados")
    if not os.path.exists(json_path):
        log(f"Arquivo {json_path} não encontrado.", erro=True)
        exit(1)

    open(LOG_PATH, "w").close()

    servico = Service(GeckoDriverManager().install())
    navegador = webdriver.Firefox(service=servico)

    try:
        log("Iniciando login no CMS...")
        login_cms(navegador, config)

        with open(json_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        total_itens = len(dados)
        for indice, item in enumerate(dados, start=1):
            titulo = item.get("Titulo", "SEM_TITULO")
            log(f"\n=== Processando item {indice} / {total_itens} ===")
            log(f"Iniciando cadastro: {titulo}")
            inicio = time.time()

            try:
                cadastrar_item(item, navegador, config)
                duracao = round(time.time() - inicio, 2)
                log(f"Cadastro finalizado com sucesso: {titulo} (tempo: {duracao}s)")
            except Exception as e:
                falhas.append(titulo)
                duracao = round(time.time() - inicio, 2)
                log(f"Erro ao processar '{titulo}' após {duracao}s: {e}", erro=True)

    finally:
        navegador.quit()

        log("\n=== RESUMO FINAL ===")
        log(f"Total de itens processados: {total_itens}")
        log(f"Total com falha: {len(falhas)}")

        if falhas:
            log("Itens com erro:")
            for titulo in falhas:
                log(f" - {titulo}", erro=True)

        print("\nProcessamento concluído. Verifique o log em log_processamento.txt")
