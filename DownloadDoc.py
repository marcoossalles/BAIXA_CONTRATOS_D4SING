import requests
import json
import wget
import os
import logging
import traceback
from dotenv import load_dotenv
import os


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO, filename='Download.log')

# Cria diretorio
def CriarDiretorio():

    try:
        # os.makedirs(caminho)
        print("Diretorio criado!")
    except FileExistsError:
        print("Diretorio já existe!")
        return {}

# Busca a lista de documentos para realizar dowload na api.
def BuscaListaParaDowload():

    api_url = "http://10.20.2.112:7014/api/Documentos/ListaDocumentosPorStatus?statusDoc=4"
    response = requests.get(api_url, verify=False)

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

# Consome a API d4sing para realizar dowload do arquivo.
def RealizaDowloadD4sing(uuidDoc):

    try:
        api_url = f"https://sandbox.d4sign.com.br/api/v1/documents/{uuidDoc}/download?tokenAPI={tokenAPI}&cryptKey={cryptKey}"
        response = requests.post(api_url)
        if response.status_code != 200:
            logging.error(f"A requisição falhou. Código de status: {response.status_code}")
            return {}

        data = response.text
        parse_json = json.loads(data)
        filename = wget.download(
            parse_json['url'], f'C:/Contratos/{uuidDoc}.zip')

        return filename
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return {} 
    
    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return {}

# Envia arquivo para ser salva
def EnviaArquivo(uuidDoc):

    files = {'file': open(f'C:\\Contratos\\{uuidDoc}.zip', 'rb')}
    response = requests.post(
        f'http://10.20.2.112:7014/api/Documentos/InsereArquivos?uuidDoc={uuidDoc}', files=files, verify=False)

    os.remove(f'C:\\Contratos\\{uuidDoc}.zip')
    try:
        if response.status_code != 201:
            logging.error(f"A requisição falhou. Código de status: {response.status_code}")
            return {}

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao realizar a requisição: {str(e)}")
        traceback.print_exc()
        return {} 
    
    except Exception as e:
        logging.error(f"Erro desconhecido: {str(e)}")
        traceback.print_exc()
        return {}

load_dotenv() # Carregar variáveis de ambiente do arquivo .env
tokenAPI =  os.getenv('tokenAPI')
cryptKey = os.getenv('cryptKey')
# Cria diretorio para salvar doc
criaDiretorio = CriarDiretorio()

# Busca a lista de documentos para dowload
listaDocParaDowload = BuscaListaParaDowload()

# Verificar se a lista esta vazia
if listaDocParaDowload is None or len(listaDocParaDowload) <= 0:
    logging.info("Nenhum Documento encontrado na lista")
    exit

else:
    # Para cada documento da lista retornado pela api
    for doc in listaDocParaDowload:
        # Realiza dowload de cada documento da lista
        realizaDowload = RealizaDowloadD4sing(doc['uuidDoc'])
        
        # Enviar arquivo para API
        if realizaDowload is None or len(realizaDowload) < 0:
            logging.info("Nenhum Documento encontrado para dowload")
            exit
        else:
            EnviaArquivo(doc['uuidDoc'])
