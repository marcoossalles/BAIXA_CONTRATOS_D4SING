import requests
import json
import logging
import traceback
from dotenv import load_dotenv
import os


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename='AlimentaLista.log')

#Busca todos os documentos.
def BuscaDoc(nPagReq=1):
    query_params = {
        'tokenAPI': f'{tokenAPI}',
        'cryptKey': f'{cryptKey}',
        'PG': nPagReq
    }

    try:
        api_response = requests.get(
            'https://sandbox.d4sign.com.br//api/v1/documents', params=query_params)
        if api_response.status_code != 200:
            logging.error(f"A requisição falhou. Código de status: {api_response.status_code}")
            return {}

        data = api_response.text
        parse_json = json.loads(data)

        return parse_json

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return {}
    
    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return {}
   
#Encaminha lista de documentos para atualizar a base de dados.
def AtualizaLista(newDoc):
    api_url = "http://10.20.2.112:7014/api/Documentos/AddInfoDocumentosInexistentes"
    try:
        response = requests.post(api_url, json=newDoc, verify=False)
        if response.status_code != 205:
            logging.error(f"A requisição falhou. Código de status: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return False
    
    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return False

    return True

#Get documentos da lista 
load_dotenv() # Carregar variáveis de ambiente do arquivo .env
tokenAPI =  os.getenv('tokenAPI')
cryptKey = os.getenv('cryptKey')
nPaginas = 1
PagAtual = 1
lContinua = True

while lContinua:
    retDocs = BuscaDoc(PagAtual)
    if len(retDocs) <= 0:
        lContinua = False
        exit

    nPaginas = retDocs[0]['total_pages']
    retDocs.pop(0)

    if AtualizaLista(retDocs) == False:
        lContinua = False
        break

    if nPaginas > PagAtual:
        PagAtual += 1
    else:
        lContinua = False
