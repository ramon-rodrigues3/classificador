from assistant import Assistant
from json import loads, JSONDecodeError
from gr_documentos import gerar_arquivo_completo
from time import sleep

def classificar_dialogos(dialogos: list) -> dict:
    try:
        assistant = Assistant('asst_kpATQ12n8mRYTxmJqewb1KaP')
    except Exception as e:
        pass

    num_dialogos = len(dialogos)
    temas = {}
    inicio = 0

    while inicio < len(dialogos):
        entrada = "\n\n".join(dialogos[inicio: inicio + 50])
        resposta = tentar(2, assistant.ask, [entrada])
        temas_encontrados = loads(resposta['text']['value'])['temas']

        num_temas = len(temas_encontrados)
        for i, tema in enumerate(temas_encontrados):
            tema_inicio = tema['indice_inicio']
            tema_fim = tema['indice_fim']
            nome_tema = tema['tema']
            dialogos_tema = dialogos[tema_inicio -1: tema_fim + 1]

            if (
                i == num_temas - 1 and tema_fim < num_dialogos 
                and num_temas > 1 and  tema_inicio != i
            ):
                inicio = tema_inicio
                break

            if nome_tema not in temas.keys():
                temas[nome_tema] = {
                    tema['subtema']: dialogos_tema
                }
            else:
                temas[nome_tema].update(
                    {
                        tema['subtema']: dialogos_tema
                    }
                )
            
            if tema_fim == num_dialogos:
                inicio = num_dialogos 
                break

    return temas


def tentar(vezes: int, funcao: callable, argumentos: list):
    for i in range(vezes):
        try:
            return funcao(*argumentos)
        except Exception as e:
            if i == vezes -1:
                raise e
            sleep(4)
