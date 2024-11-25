from openai import OpenAI

class Assistant():
    def __init__(self, assistant_id):
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.retrieve(assistant_id)
        self.thread = self.client.beta.threads.create(
            messages = []
        )
    
    def __del__(self):
        self.client.beta.threads.delete(
            self.thread.id
        )
        print("Thread encerrada!")

    def ask(self, question: str) -> str:
        self.client.beta.threads.messages.create(
            thread_id= self.thread.id,
            content=question,
            role='user'
        )
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            stream=True
        )

        for event in run:
            pass

        mensagem = self.client.beta.threads.messages.list(self.thread.id, limit=1)

        return mensagem.data[0].content[0].model_dump()
    
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

class Topico(list):
    def __init__(self, titulo):
        super.__init__(super())
        self.titulo = titulo

