import json
import requests
import time

from .exceptions import InvalidCode, InvalidCPF, InvalidResponse
from .helpers import valid_cpf

VALIDATION_URL = "https://auxilio.caixa.gov.br/api/sms/validarLogin"
LOGIN_URL = "https://auxilio.caixa.gov.br/api/cadastro/validarLogin/{cpf}"
HEADERS = {
    "content-type": "application/json; charset=utf-8"
}

# From https://stackoverflow.com/a/14620633
class AuxilioStatus(dict):
    def __init__(self, *args, **kwargs):
        super(AuxilioStatus, self).__init__(*args, **kwargs)
        self.__dict__ = self

def status(cpf, code):
    payload = json.dumps({
        "cpf": int(cpf)
     })
    request = requests.post(VALIDATION_URL, headers=HEADERS, data=payload)
    msg = request.json()['mensagem'].upper()
    
    if 'VÁLIDO' in msg:
        payload = json.dumps({
            "token": str(code)
        })
        
        request = requests.put(LOGIN_URL.format(cpf=cpf), headers=HEADERS, data=payload)
        dados = request.json()
        
        if not dados:
            raise InvalidResponse(request.text)
        
        if dados.get('codigo') == 401:
            raise InvalidCode(request.text)
        
        return AuxilioStatus(**dados)
        """
            Nome: {dados['noPessoa']}
            CPF: {dados['cpf']}
            Situação: {dados['situacao']} | {dados['nuSituacaoCadastro']}
            Motivo: {dados['motivo']}
            Banco: {dados['banco']}
            Bolsa Família: {dados['bolsa_familia']}
            Solicitação inicial: {dados['dhFinalizacaoCadastro']}
        """
    else:
        raise InvalidCPF(request.text)
