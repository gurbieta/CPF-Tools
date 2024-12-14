import time
import sys
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

continuar = True

def setup_driver():
    """Função para configurar o WebDriver (Chrome) sem o modo headless"""
    # Instala o ChromeDriver automaticamente
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def verificar_nome(nome_encontrado, primeiro_nome, cpf):
    """Função para verificar se o nome encontrado corresponde ao nome do usuário"""
    global continuar
    if primeiro_nome.lower() in nome_encontrado.lower():
        resposta = input(f"Pessoa encontrada: {nome_encontrado}. Deseja continuar? (Y/N): ").strip().upper()
        if resposta == "N":
            print(f"Nome encontrado: {nome_encontrado}. CPF: {cpf}")
            continuar = False
        return True
    return False

def consultar_cpf(driver, cpf, primeiro_nome):
    """Função para realizar a consulta de CPF e capturar o nome da pessoa"""
    driver.get("https://servicos.receita.fazenda.gov.br/servicos/cpf/consultasituacao/consultapublica.asp")

    cpf_field = driver.find_element(By.ID, "txtCPF")
    cpf_field.send_keys(cpf)

    birth_field = driver.find_element(By.ID, "txtDataNascimento")
    birth_field.send_keys("15/06/1998")

    time.sleep(1.2)

    driver.switch_to.frame(0)

    captcha_check = driver.find_element(By.ID, "checkbox")
    captcha_check.click()

    time.sleep(1)

    driver.switch_to.parent_frame()

    submit_button = driver.find_element(By.ID, "id_submit")
    submit_button.click()
    time.sleep(1)

    try:
        nome_element = driver.find_element(By.CSS_SELECTOR, "#mainComp > div:nth-child(3) > p > span:nth-child(4)")
        nome = nome_element.text
        print(f"Nome encontrado: {nome}")
        if not verificar_nome(nome, primeiro_nome, cpf):
            return nome, False  # Retorna o nome e uma flag indicando que não houve match
        return nome, True  # Retorna o nome e uma flag indicando que houve match
    except Exception as e:
        print(f"Consulta para o CPF {cpf} falhou ou não retornou nome.")
        return None, False

def processar_lista_cpfs(arquivo_cpfs, primeiro_nome):
    """Processa a lista de CPFs"""
    driver = setup_driver()
    
    with open(arquivo_cpfs, 'r') as file:
        cpfs = file.readlines()

    with open('dados_nome_cpf.txt', 'w') as arquivo_todos, open('pessoa_encontrada.txt', 'w') as arquivo_encontrados:
        for cpf in cpfs:
            if not continuar:
                break

            cpf = cpf.strip()
            if cpf:
                print(f"Consultando CPF: {cpf}")
                nome, match = consultar_cpf(driver, cpf, primeiro_nome)
                if nome:
                    # Salva todos os CPFs e nomes no arquivo 'dados_nome_cpf.txt'
                    arquivo_todos.write(f"{cpf}: {nome}\n")
                    # Se o nome der match, salva também no arquivo 'pessoa_encontrada.txt'
                    if match:
                        arquivo_encontrados.write(f"{cpf}: {nome}\n")
    
    driver.quit()

def main():
    """Função principal para manipular os argumentos do script"""
    parser = argparse.ArgumentParser(description="Bot para consultar CPFs em https://www.situacao-cadastral.com/")
    parser.add_argument("arquivo_cpfs", help="Caminho para o arquivo contendo a lista de CPFs")
    args = parser.parse_args()
    
    primeiro_nome = "NARRIMAN"
    
    processar_lista_cpfs(args.arquivo_cpfs, primeiro_nome)

if __name__ == "__main__":
    main()
