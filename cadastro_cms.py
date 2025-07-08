import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


CAMINHO_JSON = 'path to json'
CAMINHO_PROGRESO = 'path to progress.txt'  # Arquivo para salvar o progresso

#credenciais
url_login = ''
user = ''
password = ''

#url da opção para cadastro no cms
menu_cms = ''


# Carrega os dados do JSON
with open(CAMINHO_JSON, 'r', encoding='utf-8') as f:
    documentos = json.load(f)

# Lê arquivos já cadastrados
if os.path.exists(CAMINHO_PROGRESO):
    with open(CAMINHO_PROGRESO, 'r') as f:
        arquivos_cadastrados = set(l.strip() for l in f if l.strip())
else:
    arquivos_cadastrados = set()


#fluxo de cadastro
def abrir_formulario_legislacao(navegador):
    navegador.get(menu_cms)
    WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[1]/div[1]/a'))
    ).click()
    time.sleep(2)

def selecionar_categoria(navegador):
    categoria_select = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section[2]/div/form/div[1]/div[1]/select"))
    )
    select = Select(categoria_select)
    select.select_by_visible_text("Leis")

def preencher_titulo(navegador, titulo):
    titulo_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section[2]/div/form/div[1]/div[2]/div[1]/div/input'))
    )
    titulo_input.send_keys(titulo)

def preencher_texto(navegador, texto):
    campo_texto = navegador.find_element(By.XPATH, '/html/body/div[1]/div/section[2]/div/form/div[1]/div[3]/div/div[3]/div[3]')
    campo_texto.send_keys(texto)

def preencher_data(navegador, data):
    data_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="publication_date"]'))
    )
    data_input.clear()
    data_input.send_keys(data)

def adicionar_arquivo(navegador, caminho_absoluto):
    botao_adicionar = WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-adicionar"]'))
    )
    botao_adicionar.click()
    time.sleep(2)
    campo_arquivo = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="archive"]'))
    )
    print(f"Subindo o arquivo: {caminho_absoluto}")
    campo_arquivo.send_keys(caminho_absoluto)

def preencher_descricao_arquivo(navegador, descricao):
    descricao_input = WebDriverWait(navegador, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="archive[][description]"]'))
    )
    descricao_input.send_keys(descricao)

def clicar_salvar(navegador):
    botao_salvar = WebDriverWait(navegador, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-submit"]'))
    )
    print('CLicando no botão Salvar')
    botao_salvar.click()
    time.sleep(5)

def processar_documento(navegador, lei):
    abrir_formulario_legislacao(navegador)
    selecionar_categoria(navegador)
    preencher_titulo(navegador, documento["titulo"])
    preencher_texto(navegador, documento["titulo"])  # Se quiser usar outro campo, ajuste aqui
    preencher_data(navegador, documento["data"])
    caminho_absoluto = os.path.abspath(os.path.join('pdfs-teste', documento['arquivo']))
    adicionar_arquivo(navegador, caminho_absoluto)
    preencher_descricao_arquivo(navegador, documento["titulo"])
    clicar_salvar(navegador)


#iniciando o navegador
print('# INICIANDO O NAVEGADOR #')
servico = Service(GeckoDriverManager().install())
navegador = webdriver.Firefox(service=servico)

# Login
print('Acessando o CMS')
navegador.get(url_login)
navegador.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys(user)
navegador.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(password)
navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

def registrar_progresso(nome_arquivo):
    with open(CAMINHO_PROGRESO, 'a') as f:
        f.write(nome_arquivo + '\n')

for i, documento in enumerate(documentos):
    if documento['arquivo'] in arquivos_cadastrados:
        print(f"PULANDO: {documento['arquivo']} já cadastrado.")
        continue
    try:
        print(f"\n>>> [{i+1}/{len(documentos)}] Cadastrando: {documento['titulo']}")
        processar_documento(navegador, documento)
        registrar_progresso(documento['arquivo'])
    except Exception as e:
        print(f"Erro ao processar o item {i+1}: {e}")
        with open('erros.txt', 'a') as f:
            f.write(f"Erro no item {i+1} ({documento['titulo']}): {e}\n")
        continue

print("Processamento de todos os itens concluído!")
navegador.quit()
