#!/usr/bin/env python
# coding: utf-8

# In[1]:


#
# Importando bibliotecas necessarias
# 

import os
import re
import lxml
from collections import OrderedDict

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup, SoupStrainer

pd.set_option('display.max_columns', 10)


# In[4]:


#
# Definindo funcoes auxiliares
#

def gera_url(ano, serie):
    """
    Gera url para raspagem de dados. 
    
    Input
    -----
    
    ano : int 
        Entre 2009 e 2017, inclusive
        
    serie : str 
        'A' ou 'B'
        
    Output
    ------
    
    url : str 
        url de pagina com resultado de campeonato brasileiro.
    """
    url = "https://pt.wikipedia.org/wiki/" +     "Resultados_do_primeiro_turno_do_Campeonato_Brasileiro_de_Futebol_de_" +     str(ano) +     "_-_S%C3%A9rie_" +     serie.upper()
    return url
    
def raspa_pagina_atual(web_driver, ano, serie):
    """ 
    Coleta dados sobre placares e informacoes adicionais sobre a partida da atual pagina.
    
    Input 
    -----
    
    web_driver : selenium WebDriver
        web_driver em pagina gerada por 'gera_url'
    
    ano : int 
        Entre 2009 e 2017, inclusive
        
    serie : str
        'A' ou 'B'
        
    Output
    ------
    
    df_campeonato : pandas.DataFrame
        DataFrame com resultados do campeonato atual em que o web_driver se encontra.
    """ 
    trainer = SoupStrainer('table', 
                           attrs = {'style':re.compile('width:100%;\\sbackground:\\stransparent[:alnum:]*')})
    soup = BeautifulSoup(web_driver.page_source, 'lxml-xml', parse_only = trainer)
    
    tabs_com_info = soup.find_all('table')
    
    placares = [x.find_all('tr')[0].text.split('\n') for x in tabs_com_info]
    placares = [list(filter(None, x)) for x in placares]
    placares_names = ['Data','Mandante','Placar','Visitante','Estadio']

    placares_dict = OrderedDict()
    ii = 0
    for ii, zz in enumerate(placares):
        placares_dict[ii] = dict(zip(placares_names, placares[ii]))
        ii += 1

    placares_df = pd.DataFrame.from_dict(placares_dict).transpose()

    info_adicional = [x.find_all('tr')[1] for x in tabs_com_info]
    info_adicional = pd.DataFrame({'Infos' : [x.text for x in info_adicional]})

    df_campeonato = pd.concat([placares_df, info_adicional], axis = 1)
    df_campeonato = df_campeonato.assign(Ano = ano, 
                                         Serie = serie.upper(), 
                                         Campeonato = 'Brasileiro')
    return df_campeonato


# In[5]:


get_ipython().run_cell_magic('time', '', "\n#\n# Coletando os dados. Preciso ter o chromedriver ou outro driver compativel com o selenium\n#\n\nwiki = webdriver.Chrome(executable_path = r'./chromedriver')\ntodos = pd.DataFrame()\n\n\n#\n# No wikipedia, ha informacao dos campeonatos brasileiros series A e B, de 2009 -> 2017.\n#\n\nseries = ['a','b']\nanos = range(2009, 2018)\ngrid = [(ano, serie) for ano in anos for serie in series]\n\nfor ano, serie in grid:\n    wiki.get(gera_url(ano, serie))\n    todos = todos.append(raspa_pagina_atual(wiki, ano, serie))\n    \nwiki.close()")


# In[6]:


#
# Dados coletados:
#

todos = todos.reset_index().drop(columns=['index'])
todos.head()


# In[7]:


#
# Salvando para tratar a base coletada posteriormente.
#
todos.to_csv(r'./0_dados_wiki_brasileiro_raw.csv')

