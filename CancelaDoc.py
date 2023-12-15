import json
import requests
import logging
import traceback
from dotenv import load_dotenv
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO, filename='CancelaDoc.log')

def BuscaListaDocsVencidos():
    api_response = "http://10.20.2.112:7014/api/Documentos/DocumentosVencidos"
    response = requests.get(api_response, verify=False)
    try:
        if response.status_code != 200:
            logging.error(f"A requisição falhou. Código de status: {response.status_code}")
            return
        else:
            data = response.text
            return json.loads(data)

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return
    
    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return

def VerificaStatusDoc(uuidDoc):
    # busca o status do documento
    status = 0
    api_url = f"https://sandbox.d4sign.com.br/api/v1/documents/{uuidDoc}?tokenAPI={tokenAPI}&cryptKey={cryptKey}"

    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            logging.info(f"A requisição falhou. Código de status: {response.status_code}")
            return 0
        else:
            data = json.loads(response.text)
            statusStr = data[0]['statusId']
            status = int(statusStr)
            return status

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return 0

    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return 0
    
def CancelaDoc(uuidDoc):

    api_response = "https://sandbox.d4sign.com.br/api/v1/documents/"+uuidDoc + \
        "/cancel?tokenAPI={tokenAPI}&cryptKey={cryptKey}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(api_response, headers=headers)

    try:
        if response.status_code != 200:
            logging.error(f"A requisição falhou. Código de status: {response.status_code}")
            return False
        else:
            return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return False
    
    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return False

def AtualizaStatusDoc(uuidDoc, novoStatus):
    api_url = f"http://10.20.2.112:7014/api/Documentos/UpdateStatus?uuid={uuidDoc}&status={novoStatus}"

    response = requests.put(api_url, verify=False)
    try:
        if response.status_code != 204:
            logging.error(f"A requisição falhou. Código de status: {response.status_code}")
            return False
        else:
            return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return False
    
    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return False

load_dotenv() # Carregar variáveis de ambiente do arquivo .env
tokenAPI =  os.getenv('tokenAPI')
cryptKey = os.getenv('cryptKey')
# Buscar a lista de documentos vencidos
listaDocsVencidos = BuscaListaDocsVencidos()

# Verificar se a lista esta vazia
if listaDocsVencidos is None or len(listaDocsVencidos) <= 0:
    logging.info("Nenhum Documento encontrado na lista")
    exit
else:
    # Para cada documento da lista
    for doc in (listaDocsVencidos):
        # verifica o status atual do documento... já que alguns status não podem cancelar
        statusDoc = VerificaStatusDoc(doc['uuidDoc'])
        novoStatus = 0
        logging.info(f"Verificando status do documento {doc['uuidDoc']}: {statusDoc}")

        match statusDoc:
            case 0:
                exit
            case 1 | 2 | 3:
                # Enviar documento para cancelamento
                if CancelaDoc(doc['uuidDoc']):
                    novoStatus = 6
            case 4 | 5 as status:
                novoStatus = status
            case 6:
                novoStatus = 6
                logging.info(f"Novo status para o documento {doc['uuidDoc']}: {novoStatus}")
        # Se o documento for cancelado avisar ao backend
        if novoStatus != 0:
            # Atualizar status do dcumento cancelado no backenk
            retStatusCancelado = AtualizaStatusDoc(doc['uuidDoc'], novoStatus)
            logging.info(f"Status atualizado para o documento {doc['uuidDoc']}: {novoStatus}")
            # Em caso de erro enviar e-mail informando que deu erro.

