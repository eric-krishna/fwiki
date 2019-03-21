import os
import re
from datetime import datetime
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', 10)


# 
# Carregando dados
#

fwiki = pd.read_csv(r'./0_dados_wiki_brasileiro_raw.csv')

fwiki.info()
fwiki.head()


# 
# Limpeza:
#   1) remover \xa0 de algumas colunas
#   2) reescrever valores para adequar tipo das variaveis
#   3) separar 'Placar' 
#   4) separar 'Infos' em multiplas colunas
#


#
# 1) 
#

fwiki['Mandante'] = fwiki['Mandante'].str.replace('\xa0','')
fwiki['Visitante'] = fwiki['Visitante'].str.replace('\xa0','')


#
# 2) 
# 

# Ajeitando coluna Data e agregando ano para formar objeto datetime
fwiki['Data'] = (
        fwiki['Data'].
        str.replace(" de ", "-").
        str.replace("º", "").
        str.lower())

trocar_mes = {'janeiro'  :'01',
              'fevereiro':'02',
              'marco'    :'03',
              'abril'    :'04',
              'maio'     :'05',
              'junho'    :'06',
              'julho'    :'07',
              'agosto'   :'08',
              'setembro' :'09',
              'outubro'  :'10',
              'novembro' :'11',
              'dezembro' :'12'}


for mes, repl_mes in trocar_mes.items():
    fwiki['Data'] = fwiki['Data'].str.replace(mes, repl_mes)
    
fwiki['Data'] = fwiki.apply(lambda x: x['Data'] + '-' + str(x['Ano']), axis='columns')
fwiki['Data'] = pd.to_datetime(fwiki['Data'], format = "%d-%m-%Y")


# Criando variaveis Mes e Dia para fins de analise exploratoria e modelagem
fwiki = fwiki.assign(
        Mes = [x.month for x in fwiki['Data']],
        Dia = [x.day for x in fwiki['Data']])



#
# 3)
#

# Splitting Placar
placar_split = [(re.sub(u'\u2013','-',x).
                 replace('-','').
                 split()) for x in fwiki['Placar']]


# Atribuindo aa tabela
fwiki = fwiki.assign(
        GolsMandante  = [int(x[0]) for x in placar_split],
        GolsVisitante = [int(x[1]) for x in placar_split])

fwiki.drop(columns='Placar', inplace=True)

# Mandante ganhador ou nao

fwiki['GolsDiff'] = fwiki.apply(lambda x: (x['GolsMandante'] - x['GolsVisitante']), axis='columns')
fwiki['ResultadoMandante'] = (
        fwiki['GolsDiff'].
        map(np.sign).
        map({-1: 'derrota', 0: 'empate', 1: 'vitoria'}))


#
# 4)
#

split_infos = [x.split('\n\n') for x in fwiki['Infos']]

fwiki = fwiki.assign(
        Hora = [x[0].replace('\n','') for x in split_infos],
        PublicoRenda = [x[4].replace('.','').replace(' ','') for x in split_infos])

fwiki['Hora'] = fwiki['Hora'].map(lambda x: datetime.strptime(x, '%H:%M').time())

fwiki['Publico'] = fwiki['PublicoRenda'].map(lambda x: re.findall('(?<=^P.blico:)[0-9]+', x))
fwiki['Publico'] = [int(x[0]) if len(x) > 0 else np.nan for x in fwiki['Publico']]

fwiki['Renda'] = fwiki['PublicoRenda'].map(lambda x: re.findall('(?<=Renda:R\\$)[0-9]+\\.[0-9]{2}', x.replace(',','.')))
fwiki['Renda'] = [float(x[0]) if len(x) > 0 else np.nan for x in fwiki['Renda']]

fwiki.drop(columns=['Infos','PublicoRenda'], inplace=True)



#
# Tabela pronta
#

fwiki = fwiki[['Data','Ano','Mes', 'Dia', 'Serie','Campeonato','Estadio','Hora','Publico','Renda',
               'Mandante','Visitante','GolsMandante','GolsVisitante',
               'GolsDiff','ResultadoMandante']]

fwiki.to_csv(r'./1_dados_wiki_brasileiro_clean.csv', index=False)
