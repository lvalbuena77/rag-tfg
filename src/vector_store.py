"""
Este módulo se encarga de almacenar los documentos y sus embeddings
en una base de datos vectorial utilizando ChromaDB
Permite persistir los datos en disco para reutilizarlos posteriormente sin necesidad de regenerar los embeddings
"""

import shutil
import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreManager: # Clase para gestionar el almacenamiento de vectores (embeddings) utilizando ChromaDB
    def __init__(self, persist_directory="chroma_db"):
        """
        Inicializa el gestor de almacenamiento de vectores

        :param persist_directory: ruta donde se guardará la base de datos
        """
        
        self.persist_directory = persist_directory # Directorio para almacenar los datos persistentes
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2") # Carga el modelo de embeddings de HuggingFace para generar los vectores
        
    def create_vector_store(self, documents, recreate=False): # Crea la base de datos vectorial a partir de una lista de documentos
        """
        Crea e indexa los documentos en ChromaDB
        
        :param documents: lista de chunks (Document)
        :param recreate: si True, borra la base de datos existente antes de crear una nueva.
                         Usar con cuidado: elimina todos los datos previos.
        :return: objeto vector store
        """
        
        # Si recreate=True, eliminar la base de datos existente para evitar duplicados
        if recreate and os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            print(f"Base de datos existente eliminada: {self.persist_directory}")
        
        vector_store = Chroma.from_documents(
            documents=documents, # Documentos a indexar
            embedding=self.embeddings, # Modelo de embeddings para generar los vectores
            persist_directory=self.persist_directory # Directorio para almacenar la base de datos persistente
        )
        
        # ChromaDB persiste automáticamente cuando se proporciona persist_directory
        return vector_store
    
    def load_vector_store(self): # Carga la base de datos vectorial desde el disco
        """
        Carga la base de datos vectorial desde el disco
        
        :return: objeto vector store cargado
        """
        
        return Chroma(
            persist_directory = self.persist_directory, # Directorio donde se encuentra la base de datos persistente
            embedding_function = self.embeddings # Modelo de embeddings para generar los vectores al cargar la
        )
        
if __name__ == "__main__": # Prueba la creación y carga de la base de datos vectorial
    from loaders import load_documents
    from text_splitter import split_documents

    # 1 Cargar los documentos
    docs = load_documents("data/documents") # Carga los documentos desde el directorio especificado
    
    # 2 Dividir los documentos en fragmentos (chunks)
    chunks = split_documents(docs) # Divide los documentos cargados en fragmentos utilizando la función split_documents

    # 3 Crear la base de datos vectorial y almacenar los embeddings
    # NOTA: recreate=True borra y recrea la BD desde cero, evitando duplicados al re-ejecutar.
    # Usar recreate=False (defecto) si se quiere añadir documentos nuevos sin borrar los existentes.
    manager = VectorStoreManager() # Crea una instancia de la clase VectorStoreManager
    db = manager.create_vector_store(chunks, recreate=True) # recreate=True evita duplicados en re-ejecuciones
    
    print(f"Chunks indexados: {len(chunks)}")
    print("Base de datos vectorial creada y almacenada correctamente.")

    # 4 Probar la búsqueda por similitud semántica
    consultas_prueba = [
        "¿Cómo se incorpora un nuevo miembro al equipo?",
        "¿Cuáles son las buenas prácticas de desarrollo de software?",
        "¿Qué microservicios componen la arquitectura?",
    ]

    print("\n--- Prueba de búsqueda por similitud ---")
    for consulta in consultas_prueba: # Itera sobre las consultas de prueba para realizar búsquedas por similitud en la base de datos vectorial
        
        print(f"\nConsulta: {consulta}")
        resultados = db.similarity_search(consulta, k=2) # Recupera los 2 chunks más relevantes
        for i, doc in enumerate(resultados, 1):
            fuente = doc.metadata.get("source", "desconocida") # Obtiene la fuente del documento desde los metadatos, o "desconocida" si no está disponible
            fragmento = doc.page_content[:200].replace("\n", " ") # Muestra los primeros 200 caracteres del fragmento, reemplazando saltos de línea por espacios para mejor legibilidad
            print(f"  [{i}] Fuente: {fuente}")
            print(f"       Fragmento: {fragmento}...")