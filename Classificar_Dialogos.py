import streamlit as st
from assistant import Assistant
from json import loads
from io import BytesIO

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
        tema = st.selectbox('Selecionar arquivo', temas.keys())
        
        st.download_button(label=f'Baixar Arquivo: {tema}', data=gerar_arquivo(tema, temas[tema]), file_name=f'{tema}.txt')

def classificar_dialogos(dialogos: list):
    texto_barra = 'Classificando os diálogos'
    barra_progresso = st.progress(0, text=texto_barra)

    # Classificação
    assistant = Assistant('asst_kpATQ12n8mRYTxmJqewb1KaP')
    num_dialogos = len(dialogos)
    temas = {}
    inicio = 0
    print(num_dialogos)
    assert(num_dialogos == 12)

    while inicio < len(dialogos):
        

        print(f"Inicio: {inicio}, total: {num_dialogos}, razão: {inicio / num_dialogos}")
        entrada = "\n\n".join(dialogos[inicio: inicio + 6])
        resposta = assistant.ask(entrada)
        temas_encontrados = loads(resposta['text']['value'])['temas']

        for i, tema in enumerate(temas_encontrados):
            print(f'Tema encontrado: {tema}')

            if i == len(temas_encontrados) -1 and tema['indice_fim'] < num_dialogos:
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
    # {'Introdução': ['1 \n00:00:00,000 --> 00:00:04,000\nEntrevistador:\nBom dia, Sr. Carlos! Obrigado por dedicar seu tempo para essa entrevista.', '2\n00:00:04,001 --> 
    # stador:\nSr. Carlos, quais são os problemas mais urgentes que a empresa está enfrentando atualmente?']}
    texto = f"# {nome}"

    for subtema in dados.keys():
        texto += f"\n## {subtema}"
        texto_dialogo = "\n\n".join(dados[subtema])
        texto += f"\n {texto_dialogo}"
        texto += '\n'
    
    arquivo = BytesIO(bytes(texto, 'utf-8'))
    return arquivo

def main():
    st.set_page_config(page_icon="🏷")
    principal()

if __name__ == "__main__":
    main()