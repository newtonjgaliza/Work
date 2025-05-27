import json
import os
import requests
from bs4 import BeautifulSoup
import time

def create_pdfs_directory():
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')

def download_pdf(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def process_json_file(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_items = len(data)
    print(f"\nO arquivo {input_file} possui {total_items} itens")
    
    # Process each item in the JSON
    for index, item in enumerate(data, 1):
        if 'Link PDF' in item:
            # Extract filename from URL
            pdf_url = item['Link PDF']
            pdf_filename = os.path.basename(pdf_url)
            local_path = os.path.join('pdfs', pdf_filename)
            
            print(f"Baixando o arquivo do item {index} de {total_items}: {pdf_filename}")
            
            # Download the PDF
            if download_pdf(pdf_url, local_path):
                # Add the Arquivo field with the local path
                item['Arquivo'] = local_path
                print(f"✓ Download concluído: {pdf_filename}")
            else:
                item['Arquivo'] = None
                print(f"✗ Falha no download: {pdf_filename}")
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
    
    # Write the new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nArquivo {output_file} criado com sucesso!")

def main():
    print("Iniciando o processo de download dos PDFs...")
    # Create pdfs directory
    create_pdfs_directory()
    
    # Process both JSON files
    #incluir os arquivos json para leitura e escpecificar o arquivo para saida
    process_json_file('acari-leis-6_ajustado.json', 'acari-leis-6-final.json')
    

    print("\nProcesso finalizado!")

if __name__ == "__main__":
    main() 