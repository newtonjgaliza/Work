
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Variáveis globais
LOG_PATH = "log_verificacao.txt"
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

def verificar_item(item, navegador, config):
    menu_opcao = config.get('menu_opcao', 'Legislação')
    titulo = item.get("Titulo", "SEM_TITULO")

    # Clicar na opção do menu
    WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, menu_opcao))
    ).click()

    # Aguardar o campo de busca aparecer
    campo_busca = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[2]/div/div[1]/div[2]/div/label/input'))
    )
    campo_busca.clear()
    campo_busca.send_keys(titulo)
    log(f"Realizando busca por: {titulo}")

    # Esperar um pouco para o sistema aplicar o filtro
    time.sleep(2)

    try:
        # Verificar se o elemento de "nenhum resultado" está presente
        elemento_vazio = navegador.find_elements(By.XPATH, '//td[contains(@class, "dataTables_empty")]')
        if elemento_vazio:
            log(f"Item NÃO encontrado no CMS: {titulo}")
            return False

        # Verificar se existe alguma linha com dados
        linhas_resultado = navegador.find_elements(By.XPATH, '//tbody/tr')
        if linhas_resultado:
            log(f"Item encontrado no CMS: {titulo}")
            return True

        log(f"Item NÃO encontrado no CMS (sem correspondência visível): {titulo}")
        return False

    except Exception as e:
        log(f"Erro ao tentar verificar o item '{titulo}': {e}", erro=True)
        return False

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
            log(f"\n=== Verificando item {indice} / {total_itens} ===")
            inicio = time.time()

            try:
                encontrado = verificar_item(item, navegador, config)
                duracao = round(time.time() - inicio, 2)
                status = "ENCONTRADO" if encontrado else "NÃO ENCONTRADO"
                log(f"Verificação finalizada ({status}): {titulo} (tempo: {duracao}s)")
            except Exception as e:
                falhas.append(titulo)
                duracao = round(time.time() - inicio, 2)
                log(f"Erro ao verificar '{titulo}' após {duracao}s: {e}", erro=True)

    finally:
        navegador.quit()

        log("\n=== RESUMO FINAL ===")
        log(f"Total de itens processados: {total_itens}")
        log(f"Total com falha: {len(falhas)}")

        if falhas:
            log("Itens com erro:")
            for titulo in falhas:
                log(f" - {titulo}", erro=True)

        print("\nProcessamento concluído. Verifique o log em log_verificacao.txt")







'''
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

def verificar_item(item, navegador, config):
    menu_opcao = config.get('menu_opcao', 'Legislação')
    titulo = item.get("Titulo", "SEM_TITULO")

    # Clicar na opção do menu
    WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, menu_opcao))
    ).click()

    # Aguardar o campo de busca aparecer
    campo_busca = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[2]/div/div[1]/div[2]/div/label/input'))
    )

    campo_busca.clear()
    campo_busca.send_keys(titulo)
    log(f"Realizando busca por: {titulo}")

    # Esperar um pouco para o sistema filtrar os resultados
    time.sleep(2)

    # Verificar se algum resultado com o título aparece
    try:
        navegador.find_element(By.XPATH, f"//table//td[contains(text(), '{titulo}')]")
        log(f"Item encontrado no CMS: {titulo}")
        return True
    except:
        log(f"Item NÃO encontrado no CMS: {titulo}")
        return False

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
            log(f"\n=== Verificando item {indice} / {total_itens} ===")
            inicio = time.time()

            try:
                encontrado = verificar_item(item, navegador, config)
                duracao = round(time.time() - inicio, 2)
                status = "ENCONTRADO" if encontrado else "NÃO ENCONTRADO"
                log(f"Verificação finalizada ({status}): {titulo} (tempo: {duracao}s)")
            except Exception as e:
                falhas.append(titulo)
                duracao = round(time.time() - inicio, 2)
                log(f"Erro ao verificar '{titulo}' após {duracao}s: {e}", erro=True)

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
'''