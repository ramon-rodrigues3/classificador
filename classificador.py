from assistant import Assistant
from json import loads, JSONDecodeError
from tenacity import Retrying, RetryError, stop_after_attempt

def classificar_dialogos(dicionario: dict, temas_encontrados: dict) -> None:
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
