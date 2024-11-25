import streamlit as st
from google import generativeai as genai
from io import BytesIO

def gerar_transcricao(file, prompt=''):
    model = genai.GenerativeModel('gemini-1.5-flash')
    file = genai.upload_file(path=file, mime_type=f"audio/{file.name[-3:]}")
    prompt = f'{prompt}. Generate a speech transcript in SRT format. Add the name of the interlocutors if available.'

    response = model.generate_content([prompt, file])
    genai.delete_file(file.name)

    return response.text

def main():
    st.header("Transcreva audio em Texto",divider='gray')
    instrucoes = st.text_area("Instrução adicional para a transcrição")
    arquivo = st.file_uploader('Seu arquivo de áudio', ['mp3', 'wav', 'OGG'])
    gerar = st.button("Gerar transcrição srt")

    if arquivo and gerar:
        st.session_state['arquivo'] = arquivo
        transcricao = gerar_transcricao(arquivo,instrucoes)
        st.session_state['transcricao'] = transcricao
    
    if 'transcricao' in st.session_state.keys():
        transcricao = st.session_state['transcricao']
        st.divider()
        st.subheader("Baixar Transcrição")
        nome = st.text_input("Nome do arquivo")
        st.download_button('Baixar Transcrição', gerar_arquivo(transcricao), f'{nome}.txt')
        
def gerar_arquivo(texto):
    arquivo = BytesIO(bytes(texto, 'utf-8'))
    return arquivo

if __name__ == "__main__":
    main()