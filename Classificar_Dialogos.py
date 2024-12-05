import streamlit as st
from assistant import Assistant
from json import loads, JSONDecodeError
from gr_documentos import gerar_arquivo_completo
from time import sleep

def page_principal() -> None:
    st.set_page_config(page_icon="🏷")
    st.header("Classificação de Dialogos")

    arquivos = st.file_uploader("Seu arquivo", ['txt'], accept_multiple_files=True)
    executar = st.button('Executar Classificação')
    temas = st.session_state.get('temas', {})
    if arquivos and executar:
        for arquivo in arquivos:
            try: 
                conteudo = bytes.decode(arquivo.read()).replace('\r\n', '\n')
            except UnicodeDecodeError as e: 
                st.error(f"{e}: Erro ao decodificar o arquivo!")
            
            dialogos = conteudo.split('\n\n')
            temas.update(classificar_dialogos(dialogos))
            st.session_state['temas'] = temas

    st.divider()

    if len(temas.keys()) > 0:
        st.subheader("Baixar Classificações")
        tipo = st.selectbox('Selecionar tipo do arquivo', ["txt", "csv"])
        if tipo:
            st.download_button(label=f'Baixar Arquivo {tipo}', data=gerar_arquivo_completo(temas, tipo), file_name=f'classificação.{tipo}')

def classificar_dialogos(dialogos: list) -> dict:
    texto_barra = 'Classificando os diálogos'
    barra_progresso = st.progress(0, text=texto_barra)
    try:
        assistant = Assistant('asst_kpATQ12n8mRYTxmJqewb1KaP')
    except Exception as e:
        st.error(f"Erro ao se conectar a API da OpenAI: {e}")
        st.stop()

    num_dialogos = len(dialogos)
    temas = {}
    inicio = 0

    while inicio < len(dialogos):
        entrada = "\n\n".join(dialogos[inicio: inicio + 50])

        try:
            resposta = tentar(2, assistant.ask, [entrada])
        except Exception as e:
            st.error(f"Erro ao se conectar a API da OpenAI: {e}")
            st.stop()

        try:
            temas_encontrados = loads(resposta['text']['value'])['temas']
        except JSONDecodeError as e: 
            st.error(f"{e}: Erro ao decodificar a classificação!")

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
    
        barra_progresso.progress((inicio / num_dialogos), text=texto_barra)
    
    return temas

def tentar(vezes: int, funcao: callable, argumentos: list):
    for i in range(vezes):
        try:
            return funcao(*argumentos)
        except Exception as e:
            if i == vezes -1:
                raise e
            sleep(4)

def main():
    page_principal()

if __name__ == "__main__":
    main()