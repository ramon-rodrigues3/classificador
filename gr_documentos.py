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
        for tema, topicos in dados.items():
            texto += f"# {tema}\n"
            
            for topico, subtopicos in topicos.items():
                texto += f"\n## {topico}\n"
                
                for subtopico, tipos in subtopicos.items():
                    texto += f"\n### {subtopico}\n"
                    
                    for tipo, tipo_dados in tipos.items():
                        texto += f"\n#### {tipo}\n"
                        
                        descricao = tipo_dados.get("descricao", "")
                        if descricao:
                            texto += f"\nDescrição: {descricao}\n"
                        
                        if "dialogos" in tipo_dados:
                            texto_dialogo = "\n\n".join(tipo_dados["dialogos"])
                            texto += f"\n{texto_dialogo}\n"
                    
            texto += '\n----\n\n'
        
        arquivo = BytesIO(bytes(texto, 'utf-8'))
        return arquivo
    
    elif tipo == "csv":
        linhas = []
        
        for tema, topicos in dados.items():
            for topico, subtopicos in topicos.items():
                for subtopico, tipos in subtopicos.items():
                    for tipo, tipo_dados in tipos.items():
                        descricao = tipo_dados.get("descricao", "")
                        dialogos = tipo_dados.get("dialogos", [])
                        
                        for dialogo in dialogos:
                            linhas.append(
                                {
                                    "Tema": tema,
                                    "Tópico": topico,
                                    "Subtópico": subtopico,
                                    "Tipo": tipo,
                                    "Descrição": descricao,
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
