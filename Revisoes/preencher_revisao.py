#region IMPORTS
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
#endregion

arquivo_campos = '/home/newton/Vídeos/revisao/veramendes/campos_vera_mendes.json'
arquivo_respostas = '/home/newton/Vídeos/revisao/veramendes/respostas_vera_mendes.json'

#region CONFIGURAÇÃO
# Carregar arquivos JSON
with open(arquivo_campos , 'r', encoding='utf-8') as f:
    mapeamento_ids = json.load(f)

with open(arquivo_respostas , 'r', encoding='utf-8') as f:
    respostas = json.load(f)

# Configurações do CMS
estrutura = 'veramendes'
estado = 'pi'
senha_cms = ''
xpath_iniciar_revisao = '/html/body/div/div/section[2]/div[1]/div/div/div[2]/div/div[2]/div/table/tbody/tr[1]/td[6]/div/a[1]'

# Iniciar navegador
print('# INICIANDO NAVEGADOR #')
servico = Service(GeckoDriverManager().install())
navegador = webdriver.Firefox(service=servico)

# Função para preencher campos Select2 e observações
def preencher_campo(id_campo, valor):
    seletor_select2 = f"#select2-{id_campo}-container"
    tentativas = 0
    
    while tentativas < 3:
        try:
            # Selecionar opção no Select2
            select2 = WebDriverWait(navegador, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_select2))
            )
            select2.click()
            
            if valor.strip():
                campo_pesquisa = WebDriverWait(navegador, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "select2-search__field")))
                campo_pesquisa.send_keys(valor)
                campo_pesquisa.send_keys(Keys.ENTER)
            else:
                campo_pesquisa = WebDriverWait(navegador, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "select2-search__field")))
                campo_pesquisa.send_keys(Keys.ESCAPE)
            
            time.sleep(0.5)
            
            # Preencher observação se necessário
            if valor.strip().lower() == "não" or not valor.strip():
                obs_selector = f'input.observacoes-{id_campo}'
                obs_campo = WebDriverWait(navegador, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, obs_selector)))
                
                obs_campo.clear()
                if valor.strip().lower() == "não":
                    obs_campo.send_keys("Favor Informar")
                else:
                    obs_campo.send_keys("Favor Conferir")
            
            return True
            
        except StaleElementReferenceException:
            tentativas += 1
            time.sleep(1)
    
    print(f"Falha ao preencher campo {id_campo} após 3 tentativas")
    return False
#endregion

#region EXECUÇÃO PRINCIPAL
try:
    # Login no CMS
    print('## ACESSANDO CMS ##')
    navegador.get(f'https://{estrutura}.{estado}.gov.br/cms')
    navegador.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys('')
    navegador.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(senha_cms)
    navegador.find_element(By.XPATH, '/html/body/div/div[2]/form/div[3]/div[2]/button').click()

    # Acessar revisões
    print('## ACESSANDO REVISÕES ##')
    navegador.get(f'https://{estrutura}.{estado}.gov.br/cms/revisoes')
    
    # Iniciar revisão
    print('## INICIANDO REVISÃO ##')
    WebDriverWait(navegador, 20).until(
        EC.element_to_be_clickable((By.XPATH, xpath_iniciar_revisao))).click()
    
    # Aguardar carregamento do formulário
    time.sleep(3)
    
    # Preencher formulário usando os JSONs
    print('## PREENCHENDO FORMULÁRIO ##')
    for secao, campos in mapeamento_ids.items():
        print(f'\n>> SEÇÃO: {secao}')
        
        if secao in respostas:
            for item in campos:
                pergunta = list(item.keys())[0]
                id_campo = item[pergunta]
                
                # Encontrar resposta correspondente
                resposta = None
                for resp in respostas[secao]:
                    if pergunta in resp:
                        resposta = resp[pergunta]
                        break
                
                if resposta is not None:
                    # Modificação aqui: Mostrar pergunta completa junto com o ID
                    print(f'  - Campo {id_campo}: {pergunta}')
                    print(f'     Resposta: {resposta}')
                    preencher_campo(id_campo, resposta)
                    time.sleep(0.3)
    
    print('\n## REVISÃO PREENCHIDA COM SUCESSO ##')

except Exception as e:
    print(f'ERRO: {str(e)}')
    navegador.save_screenshot('erro_preenchimento.png')

finally:
    # Fechar navegador
    print(f"Revisão de {estrutura} finalizada")
    #navegador.quit()
#endregion
