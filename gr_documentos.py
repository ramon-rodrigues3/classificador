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

def gerar_arquivo_completov2(dados: dict, tipo: str):
    texto = ""
    
    if tipo == "txt":
        for tema, subtemas in dados.items():
            texto += f"# {tema}\n"
                
            for subtema, tipos in subtemas.items():
                texto += f"\n## {subtema}\n"
                
                for tipo, tipo_dados in tipos.items():
                    texto += f"\n### {tipo}\n"
                    
                    descricao = tipo_dados.get("descricao", "")
                    if descricao:
                        texto += f"\nDescrição: {descricao}\n"

                    contexto = tipo_dados.get("contexto", "")
                    if contexto:
                        texto += f"\nContexto: {descricao}\n"
                    
                    if "dialogos" in tipo_dados:
                        texto_dialogo = "\n\n".join(tipo_dados["dialogos"])
                        texto += f"\n{texto_dialogo}\n"
                
            texto += '\n----\n\n'
        
        arquivo = BytesIO(bytes(texto, 'utf-8'))
        return arquivo
    
    elif tipo == "csv":
        linhas = []
        
        for tema, subtemas in dados.items():
            for subtema, tipos in subtemas.items():
                for tipo, tipo_dados in tipos.items():
                    descricao = tipo_dados.get("descricao", "")
                    dialogos = tipo_dados.get("dialogos", [])
                    contexto = tipo_dados.get("contexto", "")
                    
                    for dialogo in dialogos:
                        linhas.append(
                            {
                                "Tema": tema,
                                "subtema": subtema,
                                "Tipo": tipo,
                                "Descrição": descricao,
                                "Contexto": contexto,
                                "Diálogo": dialogo
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
