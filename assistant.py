from openai import OpenAI
from pydantic import BaseModel
from enum import Enum

class TipoEnum(str, Enum):
    solucao = "solução"
    problema = "problema"
    outro = "outro"

class Tema(BaseModel):
    tema: str
    topico: str
    subtopico: str
    descricao: str
    tipo: TipoEnum
    indice_inicio: int
    indice_fim: int

class ListaTemas(BaseModel):
    temas: list[Tema]

class Assistant():
    def __init__(self, assistant_id) -> None:
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.retrieve(assistant_id)
        self.thread = self.thread = self.client.beta.threads.create(
            messages = []
        )
    
    def create_thread(self) -> None:
        self.thread = self.client.beta.threads.create(
            messages = []
        )

    def __del__(self) -> None:
        if self.thread:
            self.client.beta.threads.delete(
                self.thread.id
            )
            print("Thread encerrada!")

    def get_completion(self, question: str, response_format) -> dict:
        resposta = self.client.beta.chat.completions.parse(
            messages=[{'role': 'user', 'content': question}],
            model='gpt-4o',
            response_format=response_format
        )

        if resposta.choices[0].message.refusal:
            raise ValueError('GPT recusou-se a responder.')

        return resposta.choices[0].message.content

    def ask(self, question: str) -> str:
        run = self.client.beta.threads.runs.create(
            additional_messages = [
                {"role": 'user', "content": question}
            ],
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            stream=True
        )

        for event in run:
            pass

        mensagem = self.client.beta.threads.messages.list(self.thread.id, limit=1)
        return mensagem.data[0].content[0].text.value
    
    def get(self) -> object:
        response = self.client.beta.assistants.retrieve(self.assistant.id)
        return response

    def update(self, description = None, instructions = None, temperature = None) -> bool:
        try:
            _response = self.client.beta.assistants.update(
            self.assistant.id,
            description=description,
            instructions=instructions,
            temperature=temperature
            )
            return True
        except:
            return False
        
    def update_vector(self, files: list, vector_store_id: str) -> bool:
        file_ids = []
        try:
            for file in files:
                response = self.client.files.create(
                    file=file, purpose='assistants',
                )
                print(response)
                file_ids.append(response.id)
        except:
            return False
        
        try:
            response = self.client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id= vector_store_id,
                files=files,
                file_ids=file_ids
            )
            return True
        except Exception as e:
            print(e)
            return False

    def list_files(self, vector_store_id: str) -> list:
        resposta = self.client.beta.vector_stores.files.list(vector_store_id=vector_store_id)
        return resposta.data

    def remove_file(self, file_id: str) -> bool:
        try:
            response = self.client.files.delete(file_id=file_id)
            return True
        except:
            return False
