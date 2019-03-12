import re
import pandas as pd


# 
# Carregando dados
#

fwiki = pd.read_csv(r'./0_dados_wiki_brasileiro_raw.csv')

fwiki.info()
fwiki.head()


# 
# Limpeza:
#   1) reescrever valores para adequar tipo das variaveis
#   2) separar 'Placar' 
#   3) separar 'Infos' em multiplas informacoes
#


#
# 1) 
# 

# Ajeitando coluna Data e agregando ano para formar objeto datetime
fwiki.Data = (fwiki.Data
              .str.replace(" de ", "-")
              .str.replace("º", "")
              .str.lower())

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
    fwiki.Data = fwiki.Data.str.replace(mes, repl_mes)
    
fwiki.Data = fwiki.apply(lambda x: x.Data + '-' + str(x.Ano), axis='columns')
fwiki.Data = pd.to_datetime(fwiki.Data, format = "%d-%m-%Y")


# Criando variaveis Mes e Dia para fins de analise exploratoria e modelagem
fwiki = fwiki.assign(
        Mes = [x.month for x in fwiki.Data],
        Dia = [x.day for x in fwiki.Data]
        )



#
# 2)
#

# Splitting Placar
placar_split = [(re.sub(u'\u2013','-',x).
                 replace('-','').
                 split()) for x in fwiki['Placar']]


# Atribuindo aa tabela
fwiki = fwiki.assign(
        GolsMandante  = [int(x[0]) for x in placar_split],
        GolsVisitante = [int(x[1]) for x in placar_split]
        )

fwiki.drop(columns='Placar', inplace=True)


#
# 3)
#

