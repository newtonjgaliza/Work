import os
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

def formatar_data(data_texto):
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    try:
        partes = data_texto.strip().lower().split(' de ')
        dia = partes[0].zfill(2)
        mes = meses[partes[1]]
        ano = partes[2]
        return f"{dia}/{mes}/{ano}"
    except Exception as e:
        log(f"Erro ao formatar data '{data_texto}': {e}", erro=True)
        return ''

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

    data_formatada = formatar_data(item['Apresentação'])
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

    json_path = config.get("json_dados", "jsons/portarias-final.json")
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





'''
import os
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

# Função para log com arquivo e console
def log(msg, erro=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {'[ERRO]' if erro else '[INFO]'} {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

# Função para formatar a data do JSON para dd/mm/yyyy
def formatar_data(data_texto):
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    try:
        partes = data_texto.strip().lower().split(' de ')
        dia = partes[0].zfill(2)
        mes = meses[partes[1]]
        ano = partes[2]
        return f"{dia}/{mes}/{ano}"
    except Exception as e:
        log(f"Erro ao formatar data '{data_texto}': {e}", erro=True)
        return ''

# Função para login no CMS
def login_cms(navegador, config):
    navegador.get(config['cms_url'])
    WebDriverWait(navegador, 5).until(EC.presence_of_element_located((By.NAME, 'email')))
    navegador.find_element(By.NAME, 'email').send_keys(config['cms_email'])
    navegador.find_element(By.NAME, 'password').send_keys(config['cms_password'])
    navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

# Função principal para cadastrar um item no CMS
def cadastrar_item(item, navegador, config):
    WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-balance-scale'))
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

    data_formatada = formatar_data(item['Apresentação'])
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
    # Carregar configurações
    try:
        with open("config.json", "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        log("Arquivo config.json não encontrado.", erro=True)
        exit(1)

    json_path = config.get("json_dados", "jsons/portarias-final.json")
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
'''




'''
import os
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

# Função para log com arquivo e console
def log(msg, erro=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {'[ERRO]' if erro else '[INFO]'} {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

# Função para formatar a data do JSON para dd/mm/yyyy
def formatar_data(data_texto):
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    try:
        partes = data_texto.strip().lower().split(' de ')
        dia = partes[0].zfill(2)
        mes = meses[partes[1]]
        ano = partes[2]
        return f"{dia}/{mes}/{ano}"
    except Exception as e:
        log(f"Erro ao formatar data '{data_texto}': {e}", erro=True)
        return ''

# Função para login no CMS
def login_cms(navegador):
    navegador.get('https://www.acari.rn.gov.br/cms')
    WebDriverWait(navegador, 5).until(EC.presence_of_element_located((By.NAME, 'email')))
    navegador.find_element(By.NAME, 'email').send_keys('suporte@maxima.inf.br')
    navegador.find_element(By.NAME, 'password').send_keys('j5a4mQQdVGerSh')
    navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

# Função principal para cadastrar um item no CMS
def cadastrar_item(item, navegador):
    WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-balance-scale'))
    ).click()

    WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.LINK_TEXT, 'Cadastrar Legislação'))
    ).click()

    categoria_select = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.NAME, 'category_contents_id'))
    )
    Select(categoria_select).select_by_visible_text('Portarias')

    titulo_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.NAME, 'title'))
    )
    titulo_input.clear()
    titulo_input.send_keys(item['Titulo'])
    log(f"Título: {item['Titulo']}")

    data_formatada = formatar_data(item['Apresentação'])
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
    json_path = os.path.join('jsons', 'portarias-final.json')
    if not os.path.exists(json_path):
        log(f"Arquivo {json_path} não encontrado.", erro=True)
        exit(1)

    open(LOG_PATH, "w").close()

    servico = Service(GeckoDriverManager().install())
    navegador = webdriver.Firefox(service=servico)

    try:
        log("Iniciando login no CMS...")
        login_cms(navegador)

        with open(json_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        total_itens = len(dados)
        for indice, item in enumerate(dados, start=1):
            titulo = item.get("Titulo", "SEM_TITULO")
            log(f"\n=== Processando item {indice} / {total_itens} ===")
            log(f"Iniciando cadastro: {titulo}")
            inicio = time.time()

            try:
                cadastrar_item(item, navegador)
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
'''


'''
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Função para formatar a data do JSON para dd/mm/yyyy
def formatar_data(data_texto):
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    try:
        # Exemplo "25 de Março de 2025"
        partes = data_texto.strip().lower().split(' de ')
        dia = partes[0].zfill(2)
        mes = meses[partes[1]]
        ano = partes[2]
        return f"{dia}/{mes}/{ano}"
    except Exception as e:
        print(f"Erro ao formatar data '{data_texto}': {e}")
        return ''

# Função principal para cadastrar um item no CMS
def cadastrar_item(item):
    print(f"\nIniciando cadastro: {item['Titulo']}")
    servico = Service(GeckoDriverManager().install())
    navegador = webdriver.Firefox(service=servico)

    try:
        # Abrir CMS e logar
        print('Abrir CMS e logar')
        navegador.get('https://www.acari.rn.gov.br/cms')
        WebDriverWait(navegador, 5).until(EC.presence_of_element_located((By.NAME, 'email')))
        navegador.find_element(By.NAME, 'email').send_keys('suporte@maxima.inf.br')
        navegador.find_element(By.NAME, 'password').send_keys('j5a4mQQdVGerSh')
        navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

        # Navegar para Legislação
        print('Navegar para Legislação')
        WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-balance-scale'))
        ).click()

        # Clicar em Cadastrar Legislação
        print('Clicar em Cadastrar Legislação')
        WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Cadastrar Legislação'))
        ).click()

        # Selecionar categoria "Decretos"
        print('Selecionar categoria Decretos')
        categoria_select = WebDriverWait(navegador, 5).until(
            EC.presence_of_element_located((By.NAME, 'category_contents_id'))
        )
        Select(categoria_select).select_by_visible_text('Decretos')

        # Preencher título
        print('Preencher título')
        titulo_input = WebDriverWait(navegador, 5).until(
            EC.presence_of_element_located((By.NAME, 'title'))
        )
        titulo_input.clear()
        titulo_input.send_keys(item['Titulo'])
        print(f"Titulo:{item['Titulo']}")

        # Preencher data formatada
        print('Preencher data formatada')
        data_formatada = formatar_data(item['Apresentação'])
        data_input = navegador.find_element(By.ID, 'publication_date')
        data_input.clear()
        data_input.send_keys(data_formatada)
        print(f'Data de Publicação:{data_formatada}')

        # Preencher ementa (texto)
        print('Preencher Texto')
        campo_texto = navegador.find_element(By.CSS_SELECTOR, 'div.note-editable')
        campo_texto.send_keys(item['Ementa'])
        print(f"Texto:{item['Ementa']}")

        # print(' Preencher ementa (texto)')
        # campo_texto = WebDriverWait(navegador, 5).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]'))
        # )
        # #campo_texto.clear()
        # campo_texto.send_keys(item['Ementa'])

        # Adicionar arquivo
        print('Adicionar arquivo')
        botao_adicionar = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.ID, 'btn-adicionar'))
        )
        botao_adicionar.click()

        # Esperar o campo input[type=file][name="archive[][]"][class="archives form-control mb-2"] aparecer
        campo_arquivo = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[type="file"][name="archive[][]"][class="archives form-control mb-2"]')
            )
        )

        # Obter caminho absoluto do arquivo
        caminho_absoluto = os.path.abspath(item['Arquivo'])
        print(f"Subindo o arquivo: {caminho_absoluto}")

        # Enviar caminho do arquivo para o input file
        campo_arquivo.send_keys(caminho_absoluto)
        print("Arquivo enviado para upload.")

        # Agora preencher a descrição do arquivo
        descricao_input = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.NAME, 'archive[][description]'))
        )
        descricao_input.send_keys(item['Titulo'])


        # Salvar
        print('Salvar')
        botao_salvar = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.ID, 'btn-submit'))
        )
        botao_salvar.click()

        # Aguardar 2 segundos antes de fechar
        time.sleep(2)
        print(f"Cadastro finalizado: {item['Titulo']}")

    except Exception as e:
        print(f"Erro no cadastro do item '{item['Titulo']}': {e}")

    finally:
        navegador.quit()

# --- MAIN ---

if __name__ == "__main__":
    json_path = os.path.join('jsons', 'decretos-final.json')
    if not os.path.exists(json_path):
        print(f"Arquivo {json_path} não encontrado.")
        exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    for item in dados:
        cadastrar_item(item)

    print("\nProcessamento concluído para todos os itens!")
'''



'''
import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException

# Caminho para o arquivo JSON único
json_path = os.path.join('jsons', 'decretos-final.json')
if not os.path.exists(json_path):
    raise Exception("O arquivo decretos-final.json não foi encontrado na pasta jsons")

# Lendo o conteúdo do arquivo JSON
print(f"Usando o arquivo JSON: decretos-final.json")
with open(json_path, 'r', encoding='utf-8') as f:
    dados = json.load(f)

print('# INICIANDO O NAVEGADOR #')
servico = Service(GeckoDriverManager().install())
navegador = webdriver.Firefox(service=servico)

try:
    # Acessando o CMS e fazendo login
    print('Acessando o CMS')
    navegador.get('https://www.acari.rn.gov.br/cms')
    navegador.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys('suporte@maxima.inf.br')
    navegador.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys('j5a4mQQdVGerSh')
    navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

    # Clicando em Publicações
    print('Clicando em Legislação')
    WebDriverWait(navegador, 8).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-balance-scale'))
    ).click()

    print('Clicando em Cadastrar Legislação')
    WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[1]/div[1]/a'))
    ).click()

    print("Escolhendo a categoria")
    categoria_select = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.NAME, "category_contents_id"))
    )
    select = Select(categoria_select)
    select.select_by_visible_text("Decretos")

    print("Preenchendo o Título")
    titulo_input = WebDriverWait(navegador, 5).until(
         EC.presence_of_element_located((By.NAME, "title"))
    )
    titulo_input.send_keys(dados['Titulo'])

    print('Preenchendo a data de publicação')
    # Convertendo "28 de Setembro de 2012" para "28/09/2012"
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    try:
        dia, mes_nome, ano = dados['Apresentação'].strip().split(' de ')
        mes_num = meses[mes_nome.lower()]
        data_formatada = f"{dia.zfill(2)}/{mes_num}/{ano}"
    except Exception as e:
        raise Exception(f"Erro ao converter a data: {dados['Apresentação']} - {e}")

    data_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.ID, 'publication_date'))
    )
    data_input.clear()
    data_input.send_keys(data_formatada)

    print('Preenchendo o Texto')
    campo_texto = navegador.find_element(By.XPATH, '/html/body/div[1]/div/section[2]/div/form/div[1]/div[3]/div/div/div[3]/div[3]')
    campo_texto.send_keys(dados['Ementa'])

    print('Adicionar o Arquivo')
    botao_adicionar = WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-adicionar"]'))
    )
    botao_adicionar.click()

    time.sleep(2)

    campo_arquivo = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"][name="archive[][]"][class="archives form-control mb-2"]'))
    )
    caminho_absoluto = os.path.abspath(dados['Arquivo'])
    print(f"Subindo o arquivo: {caminho_absoluto}")
    campo_arquivo.send_keys(caminho_absoluto)

    descricao_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="archive[][description]"]'))
    )
    descricao_input.send_keys(dados['Titulo'])

    time.sleep(5)

    botao_salvar = WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-submit"]'))
    )
    botao_salvar.click()

    time.sleep(5)

except Exception as e:
    print(f"Erro ao processar o arquivo decretos-final.json: {e}")

finally:
    print("Fechando o navegador")
    navegador.quit()

print("\nProcessamento concluído!")
'''




'''
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

#### função acessar cms #####

# Inicializando o Navegador
print('# INICIANDO O NAVEGADOR #')
servico = Service(GeckoDriverManager().install())
navegador = webdriver.Firefox(service=servico)

#### função ler json ####
with open('decretos-final.json', 'r', encoding='utf-8') as f:
    decretos = json.load(f)
#### fim da função ler json ####




# Acessando o CMS e fazendo login
print('Acessando o CMS')
navegador.get('https://www.acari.rn.gov.br/cms')
navegador.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys('suporte@maxima.inf.br')
navegador.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys('j5a4mQQdVGerSh')
navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()
####### fim da função acessar o cms ####

#### função clicar no menu ####
# Clicando em Publicações
print('Clicando no menu Legislação')
WebDriverWait(navegador, 5).until(
   EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-balance-scale'))
).click()
####  fim da função clicar no menu   ####


#### função clicando em Cadastrar ####
print('Clicando em Cadastrar')
WebDriverWait(navegador, 5).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[1]/div[1]/a'))
).click()
#### fim da função clicando em Cadastrar ####

#### função selecionando campo Categoria ####
print("Escolhendo a categoria")
# Aguarda o elemento select estar presente
categoria_select = WebDriverWait(navegador, 10).until(
    EC.presence_of_element_located((By.ID, "category_contents_id"))
)

# Cria um objeto Select
select = Select(categoria_select)

# Seleciona a opção "Decretos"
select.select_by_visible_text("Decretos")
#### fim da função selecionando campo Categoria ####

#### função preenchendo o titulo #### 
for decreto in decretos:
    print("Preenchendo o Título")
    titulo_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.ID, "title"))
    )
    titulo_input.clear()  # limpa o campo antes de digitar
    titulo_input.send_keys(decreto['Titulo'])



#### final do processon ####
print('---- FIM ----')



'''