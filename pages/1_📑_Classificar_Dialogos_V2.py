import streamlit as st
import gr_documentos as grd
from assistant import Assistant
import json
from tenacity import stop_after_attempt, wait_fixed, retry_if_exception_type, retry
from pydantic import BaseModel
from enum import Enum

class TipoEnum(str, Enum):
    solucao = "solução"
    problema = "problema"
    outro = "outro"

class ContextoEnum(str, Enum):
    no_contexto = "No contexto"
    fora_do_contexto = "Fora do contexto"

class Tema(BaseModel):
    tema: str
    subtema: str
    descricao: str
    contexto: ContextoEnum
    tipo: TipoEnum
    indice_inicio: int
    indice_fim: int

class ListaTemas(BaseModel):
    temas: list[Tema]

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), retry=retry_if_exception_type(Exception))
def solicitar_assistente(assistant: Assistant, entrada: str, lista):
    return assistant.ask(entrada)

def atualizar_classificacao(dicionario: dict, temas_encontrados: list, dialogos: list) -> None:
    for item in temas_encontrados:
        tema = item.get('tema')
        subtema = item.get('subtema')
        tipo = item.get('tipo')
        descricao = item.get('descricao')
        contexto = item.get('contexto')
        ind_inicio = item.get('indice_inicio') - 1
        ind_fim = item.get('indice_fim') - 1
        trecho = dialogos[ind_inicio: ind_fim + 1]

        tema_dados = dicionario.setdefault(tema, {})
        subtopico_dados = tema_dados.setdefault(subtema, {})
        tipo_dados = subtopico_dados.setdefault(tipo, {"dialogos": [], "descricao": ""})

        tipo_dados["dialogos"].extend(trecho)
        tipo_dados["descricao"] = descricao
        tipo_dados["contexto"] = contexto

def page_principal() -> None:
    st.subheader("Enviar Arquivo", divider="gray")

    arquivos = st.file_uploader("Seus arquivos", ['txt', 'srt'], accept_multiple_files=True)
    executar = st.button('Executar Classificação')

    if arquivos and executar:
        classificacao = st.session_state.get('classificacao_v2', {})
        try:
            assistant = Assistant('asst_kpATQ12n8mRYTxmJqewb1KaP') 
        except Exception as e:
            st.error(f'Erro ao instânciar assistente. Erro: {e}')
            st.stop()

        for arquivo in arquivos:
            st.markdown(f'-> {arquivo.name}')
            progresso = st.progress(0, 'Classificando arquivo...')

            try:
                conteudo = arquivo.read().decode('utf-8').replace('\r\n', '\n').split('\n\n')
            except UnicodeDecodeError as e:
                st.error(f'Erro ao decodificar arquivo {arquivo.name}. Verifique se ele está codificado em utf-8')
                st.stop()
            except Exception as e:
                st.error(f'Erro inesperado! Erro: {e}')
            
            dialogos = [dialogo for dialogo in conteudo if not dialogo.isspace()]
            num_dialogos = len(dialogos)
            inicio = 0
            
            while inicio < num_dialogos - 1:
                entrada = "\n\n".join(dialogos[inicio: inicio + 100])

                try:
                    response = solicitar_assistente(assistant, entrada, classificacao.keys())
                except Exception as e:
                    print(e)
                    st.error(f'Erro de conexão ao GPT após múltiplas tentativas. Erro {e}')
                    st.stop()

                print(f"\n {response} \n") 

                try:
                    temas_encontrados = json.loads(response)['temas']
                except json.decoder.JSONDecodeError as e:
                    print(e)
                    st.warning('A IA deu uma resposta inesperada durante a classificação. Tente novamente!')
                    st.stop() 
                except:
                    st.markdown(type(response))
                
                num_temas = len(temas_encontrados)
                
                if num_temas == 0:
                    print('A ia respondeu com uma lista vazia')
                    inicio += 100
                    continue
                    # st.warning('A IA deu uma resposta inesperada durante a classificação. Tente novamente!')
                    # st.stop() 

                try:
                    ultimo_tema = temas_encontrados[-1]
                    ut_indice_inicio = ultimo_tema['indice_inicio']
                    ut_indice_fim = ultimo_tema['indice_fim']
                    if not isinstance(ut_indice_inicio, int) or not isinstance(ut_indice_fim, int):
                        raise TypeError('Tipo incompatível')
                except Exception as e:
                    print(e)
                    st.warning('A IA deu uma resposta inesperada durante a classificação. Tente novamente!')
                    st.stop()
                
                try: 
                    if num_temas > 1 and temas_encontrados[-1]['indice_fim'] < num_dialogos:
                        if ut_indice_inicio <= inicio:
                            raise ValueError('Valor inválido. Loop infinito evitado.')
                        temas_encontrados = temas_encontrados[:-1]
                        atualizar_classificacao(classificacao, temas_encontrados, dialogos)
                        inicio = ut_indice_inicio - 1
                    else:
                        if ut_indice_fim <= inicio:
                            raise ValueError('Valor inválido. Loop infinito evitado.')
                        atualizar_classificacao(classificacao, temas_encontrados, dialogos)
                        inicio = ut_indice_fim - 1
                except Exception as e:
                    print(e)
                    st.warning('A IA deu uma resposta inesperada durante a classificação. Tente novamente!')
                    st.stop()

                final = inicio + 101 if inicio + 101 < num_dialogos else num_dialogos
                progresso.progress(inicio/num_dialogos, f'classificando diálogos {inicio + 1}  a {final}...')
            progresso.progress(1.0, 'Classificação Concluída.')
        st.session_state['classificacao_v2'] = classificacao
        st.success("Classificação bem sucedida!")

@st.fragment
def page_classificacao() -> None:
    st.subheader("Download", divider="gray")
    temas = st.session_state.get('classificacao_v2', {})

    if len(temas.keys()) > 0:

        tipo = st.selectbox('Selecionar tipo do arquivo', ["txt", "csv"])
        
        if tipo:
            st.download_button(label=f'Baixar Arquivo {tipo}', data=grd.gerar_arquivo_completov2(temas, tipo), file_name=f'classificação.{tipo}')
    else:
        st.info("Nenhuma classificação registrada.")

def main():
    st.set_page_config(layout='wide')
    colunas = st.columns(2, gap='large')

    with colunas[0]:
        page_principal()
    with colunas[1]:
        page_classificacao()

if __name__ == "__main__":
    main()