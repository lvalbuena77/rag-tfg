"""
Este módulo se encarga de generar embeddings (representaciones vectoriales)
a partir de los fragmentos de texto (chunks).
Utiliza el modelo 'all-MiniLM-L6-v2' de Sentence Transformers para crear los embeddings,
optimizado para tareas de similitud semántica y recuperación de información.

"""
from sentence_transformers import SentenceTransformer

class EmbeddingsGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Inicializa el modelo de embeddings

        :param model_name: nombre del modelo a utilizazar
        """
        self.model = SentenceTransformer(model_name) # Carga el modelo de Sentence Transformers para generar embeddings

    def generate_embeddings(self, documents):
        """
        Genera embeddings para una lista de documentos (chunks)

        :param documents: lista de objetos Document de LangChain
        :return: lista de vectores (embeddings) correspondientes a cada documento
        """
        
        texts = [doc.page_content for doc in documents] # Extrae el contenido textual de cada documento (chunk)
        
        embeddings = self.model.encode(texts, show_progress_bar=True) # Genera los embeddings utilizando el modelo cargado, mostrando una barra de progreso
        
        return embeddings
    
if __name__ == "__main__": # Prueba la generación de embeddings
    from loaders import load_documents
    from text_splitter import split_documents

    docs = load_documents("data/documents") # Carga los documentos desde el directorio especificado
    chunks = split_documents(docs) # Divide los documentos cargados en fragmentos utilizando la función split_documents

    embedder = EmbeddingsGenerator() # Crea una instancia de la clase EmbeddingsGenerator
    embeddings = embedder.generate_embeddings(chunks) # Genera los embeddings para los fragmentos utilizando el método generate_embeddings

    print(f"Embeddings generados: {len(embeddings)}")