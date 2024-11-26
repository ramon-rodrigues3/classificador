import streamlit as st
from assistant import Assistant
from json import loads
from io import BytesIO
import pandas as pd

def principal():
    st.header("Classificação de Dialogos")

    arquivo = st.file_uploader("Seu arquivo", ['txt'])
    executar = st.button('Executar Classificação')
    temas = st.session_state.get('temas', {})

    if arquivo and executar:
        conteudo = bytes.decode(arquivo.read()).replace('\r\n', '\n')
        dialogos = conteudo.split('\n\n')
        temas = classificar_dialogos(dialogos)
        st.session_state['temas'] = temas

    st.divider()

    if len(temas.keys()) > 0:
        st.subheader("Baixar Classificações")
        tipo = st.selectbox('Selecionar tipo do arquivo', ["txt", "csv"])
        if tipo:
            st.download_button(label=f'Baixar Arquivo {tipo}', data=gerar_arquivo_completo(temas, tipo), file_name=f'classificação.{tipo}')

def classificar_dialogos(dialogos: list):
    texto_barra = 'Classificando os diálogos'
    barra_progresso = st.progress(0, text=texto_barra)

    # Classificação
    assistant = Assistant('asst_kpATQ12n8mRYTxmJqewb1KaP')
    num_dialogos = len(dialogos)
    temas = {}
    inicio = 0
    print(num_dialogos)
    #assert(num_dialogos == 12)

    while inicio < len(dialogos):
        print(f"Inicio: {inicio}, total: {num_dialogos}, razão: {inicio / num_dialogos}")
        entrada = "\n\n".join(dialogos[inicio: inicio + 50])
        resposta = assistant.ask(entrada)
        temas_encontrados = loads(resposta['text']['value'])['temas']

        for i, tema in enumerate(temas_encontrados):
            print(f'Tema encontrado: {tema}')

            if i == len(temas_encontrados) -1 and tema['indice_fim'] < num_dialogos and len(temas_encontrados) > 1:
                inicio = tema['indice_inicio']
                break

            if tema['tema'] not in temas.keys():
                temas[tema['tema']] = {tema['subtema']: dialogos[tema['indice_inicio'] -1: tema['indice_fim'] + 1]}
            else:
                temas[tema['tema']].update(
                {tema['subtema']: dialogos[tema['indice_inicio'] -1: tema['indice_fim'] + 1]})
            
            if tema['indice_fim'] == num_dialogos:
                inicio = num_dialogos 
                print(f'Fim!')
                break
    
        barra_progresso.progress((inicio / num_dialogos), text=texto_barra)
    return temas

def gerar_arquivo(nome: str, dados: dict):
    texto = f"# {nome}"

    for subtema in dados.keys():
        texto += f"\n## {subtema}"
        texto_dialogo = "\n\n".join(dados[subtema])
        texto += f"\n {texto_dialogo}"
        texto += '\n'
    
    arquivo = BytesIO(bytes(texto, 'utf-8'))
    return arquivo

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

def main():
    st.set_page_config(page_icon="🏷")
    principal()

if __name__ == "__main__":
    main()