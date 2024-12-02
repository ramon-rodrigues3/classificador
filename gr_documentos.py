from io import BytesIO
import pandas as pd

def gerar_arquivo_completo(dados: dict, tipo: str):
    texto = ""
    if tipo == "txt":
        for tema in dados.keys():
            texto += f"# {tema}\n"

            for subtema in dados[tema].keys():
                texto += f"\n## {subtema}"
                texto_dialogo = "\n\n".join(dados[tema][subtema])
                texto += f"\n {texto_dialogo}\n"
            texto += '\n----\n\n'
               
        arquivo = BytesIO(bytes(texto, 'utf-8'))

        return arquivo
    
    if tipo == "csv":
        linhas = []
        
        for tema in dados.keys():
            for subtema in dados[tema].keys():
                for dialogo in dados[tema][subtema]:
                    linhas.append(
                        {
                            "Tema": tema,
                            "Subtema": subtema,
                            "Dialogo": dialogo
                        }
                    )
        df = pd.DataFrame(linhas)
        arquivo = BytesIO()
        df.to_csv(arquivo, index=False, sep=";")

        return arquivo
    
def gerar_arquivo(nome: str, dados: dict):
    texto = f"# {nome}"

    for subtema in dados.keys():
        texto += f"\n## {subtema}"
        texto_dialogo = "\n\n".join(dados[subtema])
        texto += f"\n {texto_dialogo}"
        texto += '\n'
    
    arquivo = BytesIO(bytes(texto, 'utf-8'))
    return arquivo
