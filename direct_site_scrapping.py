from pandas.core.dtypes import base
from selenium import webdriver
import time
import pandas as pd
from pandas import DataFrame
from selenium.webdriver.support.ui import Select
from pathlib import Path
import os.path


# carregando driver e passando endereço
driver = webdriver.Chrome("/home/arch/Downloads/chromedriver")
driver.implicitly_wait(3)
pagina = 'https://transparencia.fortaleza.ce.gov.br/index.php/despesa/acompanhamentoExecucaoOrcamentaria'


def declarar_variaveis_globais():
  global unidades_orcamentarias
  global funcoes
  global subfuncoes
  global programas
  global acoes
  global elementos_de_despesa
  global fontes


  unidades_orcamentarias = {}
  funcoes = {}
  subfuncoes = {}
  programas = {}
  acoes = {}
  elementos_de_despesa = {}
  fontes = {}

# Abre e prepara a página inicial para iniciar uma pesquisa
# Parâmetros: index_ano indica que ano será aberto. O valor é um número
# que indica a posição do ano na caixa select de ano da página 
def seta_pagina(index_ano):
  # abrindo página
  driver.get(pagina) 
  # setando meses
  Select(driver.find_element_by_id('cboMesIni')).select_by_index(0)
  Select(driver.find_element_by_id('cboMesFim')).select_by_index(11)
  exercicio = Select(driver.find_element_by_id('cboExercicio'))
  # seta exercício para a posição index_ano
  exercicio.select_by_index(index_ano)
  time.sleep(0.5)

# Auto explicativo
# Parâmetros: dicionario tem de ser global
def adicionar_ao_dicionario(termo, dicionario, ano):
  termo_pronto = termo.split(maxsplit=2)
  if ano in dicionario:
    # Faz nada
    pass
  else:
    dicionario[ano] = {}

  if termo[0] in dicionario[ano]:
    # Faz nada
    pass
  else:
    dicionario[ano][termo_pronto[0]] = termo_pronto[2]
  print("dicio")
  print(dicionario)

# Select são filtros em um form
# Options são as opções disponíveis
def obter_elementos_de_select(select_id):
  select = driver.find_element_by_id(select_id)
  list_of_elements = []
  for e in select.find_elements_by_tag_name("option"):
    if e.text != '':
      list_of_elements.append(e.text)
  return list_of_elements

def configuracao_padrao():
  seta_pagina(0)
  declarar_variaveis_globais()

  global filtro_anos
  filtro_anos = driver.find_element_by_id('cboExercicio')
  global todos_anos
  todos_anos = filtro_anos.find_elements_by_tag_name("option")
  
  # endereco onde estão os arquivos
  global current_directory
  current_directory = os.getcwd()

def variaveis_do_orgao():
  time.sleep(0.5)
  # seleção via id
  global filtro_orgao
  filtro_orgao = driver.find_element_by_id('filtroPorOrgao')
  # coleta todas opções de um elemento
  global todos_orgaos
  todos_orgaos = filtro_orgao.find_elements_by_tag_name("option")
  
  filtro_orgao.find_elements_by_tag_name("option")
  global total_de_orgaos
  total_de_orgaos = len(todos_orgaos) - 1 #retirando opção em branco

def atualizar_dicionarios(ano):
  # Adicionando funções
  elementos = obter_elementos_de_select('cboFuncao')
  print(elementos)
  for elemento in elementos:
    if (elemento != ''):
      adicionar_ao_dicionario(elemento, funcoes, ano)

  elementos = obter_elementos_de_select('cboSubFuncao')
  for elemento in elementos:
    if (elemento != ''):
      adicionar_ao_dicionario(elemento, subfuncoes, ano)
  
  elementos = obter_elementos_de_select('cboAcao')
  for elemento in elementos:
    if (elemento != ''):
      adicionar_ao_dicionario(elemento, acoes, ano)

  elementos = obter_elementos_de_select('cboElemDesp')
  for elemento in elementos:
    if (elemento != ''):
      adicionar_ao_dicionario(elemento, elementos_de_despesa, ano)
  
  elementos = obter_elementos_de_select('cboFonte')
  for elemento in elementos:
    if (elemento != ''):
      adicionar_ao_dicionario(elemento, fontes, ano)

def status_atual(ano, total, orgao_atual):
  print("Ano " + str(ano) + "|" + str(i) + "/" + str(total - 1) + " - " + str(orgao_atual))

def obter_nome_do_orgao_selecionado(index_orgao):
  time.sleep(0.5)
  select = Select(driver.find_element_by_id('filtroPorOrgao'))
  select.select_by_index(index_orgao)
  return select.first_selected_option.get_attribute("text").replace("/", " - ")

def click_em_submit():
  driver.find_element_by_xpath('/html/body/div[2]/main/div[2]/form/div[8]/input').click() #submit
  time.sleep(0.5)

# Métodos genéricos para datascraping
def obter_texto_de_elemento(linha, coluna):
  return linha.find_elements_by_tag_name("td")[coluna].text

def gerar_arquivo_do_orgao(index_ano, orgao_atual):
  path = os.path.join(current_directory, "coleta_aprimorada_por_ano/" + str(index_ano+2010))
  linhas = driver.find_elements_by_xpath('//table/tbody/tr')
  base_de_dados = pd.DataFrame(columns = ['Ano', 'Unidade Orçamentária', 'Função', 'Subfunção', 'Programa', 'Ação', 'Elemento', 'Fonte', 'Saldo Inicial', 'Saldo Atual', 'Emp. no Mês', 'Emp. até Mês', 'Liq. no Mês', 'Liq. até Mês', 'Pago no Mês', 'Pago até Mês', 'Saldo a Utilizar'])
  if len(linhas) > 0:
    for linha in linhas:
      qtd_colunas = len( linha.find_elements_by_tag_name("td") )
      linha_a_inserir = [index_ano + 2010]
      # se possui informações até Fonte
      if obter_texto_de_elemento(linha, 6) != '':
        for coluna in range(qtd_colunas):
          # parte numéricas          
          if coluna >= 7:
            linha_a_inserir.append( float(obter_texto_de_elemento(linha, coluna).replace(".", "").replace(",", ".")) )
          # Função
          elif coluna == 1:
            pass
          # subfunção
          elif coluna == 2:
            pass
          # programa
          elif coluna == 3:
            pass
          # ação
          elif coluna == 4:
            pass
          # elemento
          elif coluna == 5:
            pass
          # fonte
          elif coluna == 6:
            pass
          # texto comum
          else:
            linha_a_inserir.append( obter_texto_de_elemento(linha, coluna) )
        # print(linha_a_inserir)
        dados_novos = pd.Series( linha_a_inserir, index = base_de_dados.columns )
        base_de_dados = base_de_dados.append(dados_novos, ignore_index=True )
    # path do arquivo
    
    folder = Path(path)
    if (folder.exists() == False):
      os.makedirs(path)

    # verifica se arquivo existe
    if os.path.isfile(path + '/' + orgao_atual + '.csv'):
      # testando nomes alternativos
      verificador_de_repeticao = 1
      arquivo_existente = True
      while arquivo_existente:
        if os.path.isfile(path + '/' + orgao_atual + ' ' + str(verificador_de_repeticao) + ' '  + '.csv'):
          verificador_de_repeticao += 1
        else:
          nome_do_arquivo = path + '/' + orgao_atual + ' ' +  str(verificador_de_repeticao) + ' '  + '.csv'
          arquivo_existente =  False
    else:
      nome_do_arquivo = path + '/' + orgao_atual + '.csv'

    print(base_de_dados)
    # base_de_dados.to_csv(nome_do_arquivo, index=False)


def coleta_por_ano(ano=2010):
  print("===========================")
  print("COLETA DE DADOS DO ANO "+str(ano))
  print("===========================")
  print("")
  index_do_ano = ano - 2010
  configuracao_padrao()
  exercicio = Select(driver.find_element_by_id('cboExercicio'))
  exercicio.select_by_index(index_do_ano)
  variaveis_do_orgao()
  # atualizar_dicionarios(ano)
  time.sleep(0.5)
  for i in range(total_de_orgaos):
    if i != 0:
      orgao_atual = obter_nome_do_orgao_selecionado(i)
      print("Ano " + str(ano) + "|" + str(i) + "/" + str(total_de_orgaos - 1) + " - " + str(orgao_atual))
      click_em_submit()
      gerar_arquivo_do_orgao(index_do_ano, orgao_atual)
    seta_pagina(index_do_ano)
  print("===============")
  print("COLETA COMPLETA")
  print("===============")

def mudar_select_e_esperar(id, valor):
  select = Select(driver.find_element_by_id(id)) 
  select.select_by_value(valor)

  time.sleep(0.5)

def informar_andamento(elemento, lista, classificacao):
  print(f'{classificacao} - {elemento} - {lista.index(elemento) + 1}/{len(lista)}')

def preencher_dicionarios(anos):
  print('===Preenchendo Dicionários===')
  for ano in anos:
    informar_andamento(ano, anos, 'Ano')
    # modificar ano para o desejado
    mudar_select_e_esperar('cboExercicio', str(ano))
    orgaos_no_select = obter_elementos_de_select('filtroPorOrgao')
    print(orgaos_no_select)
    # print(f'{len(orgaos_no_select)} órgãos encontrados')
    for orgao in orgaos_no_select:
      adicionar_ao_dicionario(orgao, dicionario, ano)
      informar_andamento(orgao, orgaos_no_select, 'Órgão')


    # coletar dados dos órgãos
    

driver.get(pagina) 
preencher_dicionarios(range(2010, 2021))
for ano in range(2010, 2021):
  coleta_por_ano(ano)

# coleta_por_ano(2021)
