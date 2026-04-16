"""
Este módulo implementa la recuperación de fragmentos relevantes
mediante búsqueda híbrida: combina búsqueda vectorial semántica (ChromaDB)
con búsqueda léxica por palabras clave (BM25), ponderando ambas señales
para mejorar la precisión en términos técnicos y nombres específicos.
"""

from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from vector_store import VectorStoreManager


class RetrieverManager:
    def __init__(
        self,
        persist_directory: str = "chroma_db",
        k: int = 4,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4,
    ):
        """
        Inicializa el gestor de recuperación híbrida.

        :param persist_directory: ruta de la base de datos vectorial ChromaDB
        :param k: número de fragmentos a recuperar por cada retriever
        :param vector_weight: peso de la búsqueda vectorial (0.0 - 1.0)
        :param bm25_weight: peso de la búsqueda léxica BM25 (0.0 - 1.0)
        """
        if abs(vector_weight + bm25_weight - 1.0) > 1e-6:
            raise ValueError("vector_weight + bm25_weight debe ser igual a 1.0")

        self.persist_directory = persist_directory # Directorio donde se encuentra la base de datos vectorial ChromaDB
        self.k = k # Número de fragmentos a recuperar por cada retriever (vectorial y BM25)
        self.vector_weight = vector_weight # Peso asignado a la búsqueda vectorial en la combinación híbrida (entre 0.0 y 1.0)
        self.bm25_weight = bm25_weight # Peso asignado a la búsqueda léxica BM25 en la combinación híbrida (entre 0.0 y 1.0)

    def get_retriever(self) -> EnsembleRetriever: # Construye y devuelve el retriever híbrido combinando búsqueda vectorial y BM25
        """
        Construye y devuelve el retriever híbrido.

        Carga el índice vectorial desde disco, reconstruye el índice BM25
        a partir de los chunks almacenados en ChromaDB y los combina
        mediante EnsembleRetriever con los pesos configurados.

        :return: EnsembleRetriever listo para recibir consultas
        """
        # Cargar la base de datos vectorial desde disco
        store_manager = VectorStoreManager(persist_directory=self.persist_directory) # Crear una instancia del gestor de almacenamiento de vectores para acceder a ChromaDB
        db = store_manager.load_vector_store() # Cargar la base de datos vectorial desde el directorio persistente especificado (ChromaDB)

        # Retriever vectorial (búsqueda semántica por similitud coseno)
        vector_retriever = db.as_retriever(
            search_kwargs={"k": self.k}  # Devuelve los k chunks más cercanos semánticamente
        )

        # Reconstruir el corpus de chunks desde ChromaDB para BM25
        # (BM25 es un índice en memoria, no persistente)
        result = db._collection.get(include=["documents", "metadatas"])
        all_docs = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(result["documents"], result["metadatas"])
        ]

        # Retriever léxico BM25 (búsqueda por coincidencia de términos)
        bm25_retriever = BM25Retriever.from_documents(all_docs)
        bm25_retriever.k = self.k  # Devuelve los k chunks con mayor puntuación BM25

        # Retriever híbrido: combina ambas señales con sus pesos respectivos
        hybrid_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[self.vector_weight, self.bm25_weight],
        )

        return hybrid_retriever


# if __name__ == "__main__":  # Prueba el retriever híbrido sobre el corpus indexado
#     retriever_manager = RetrieverManager(k=4, vector_weight=0.6, bm25_weight=0.4)
#     retriever = retriever_manager.get_retriever()

#     consultas_prueba = [
#         "¿Cómo se incorpora un nuevo miembro al equipo?",
#         "¿Cuáles son las buenas prácticas de desarrollo de software?",
#         "¿Qué microservicios componen la arquitectura?",
#         "¿Cuáles son las políticas de seguridad de la información?",
#     ]

#     print("\n--- Prueba del retriever híbrido (vectorial 60% + BM25 40%) ---")
#     for consulta in consultas_prueba:
#         print(f"\nConsulta: {consulta}")
#         resultados = retriever.invoke(consulta)  # Lanza la búsqueda híbrida
#         resultados = resultados[:4]  # Limitar a los 4 resultados más relevantes (combinados)
#         for i, doc in enumerate(resultados, 1):
#             fuente = doc.metadata.get("source", "desconocida")
#             fragmento = doc.page_content[:200].replace("\n", " ")
#             print(f"  [{i}] Fuente: {fuente}")
#             print(f"       Fragmento: {fragmento}...")

if __name__ == "__main__":
    retriever_manager = RetrieverManager(k=4, vector_weight=0.6, bm25_weight=0.4)

    # Cargar componentes
    store_manager = VectorStoreManager()
    db = store_manager.load_vector_store()

    vector_retriever = db.as_retriever(search_kwargs={"k": 4})

    result = db._collection.get(include=["documents", "metadatas"])
    all_docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(result["documents"], result["metadatas"])
    ]

    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = 4

    retriever = retriever_manager.get_retriever()

    consultas_prueba = [
        "¿Cómo se incorpora un nuevo miembro al equipo?",
        "¿Cuáles son las buenas prácticas de desarrollo de software?",
        "¿Qué microservicios componen la arquitectura?",
        "¿Cuáles son las políticas de seguridad de la información?",
    ]

    for consulta in consultas_prueba:
        print("\n" + "="*60)
        print(f"CONSULTA: {consulta}")

        # 🔵 1. VECTORIAL
        print("\n--- RESULTADOS VECTORIALES ---")
        resultados_vector = vector_retriever.invoke(consulta)
        for i, doc in enumerate(resultados_vector, 1):
            print(f"[{i}] {doc.metadata.get('source')}")

        # 🟡 2. BM25
        print("\n--- RESULTADOS BM25 ---")
        # resultados_bm25 = bm25_retriever.get_relevant_documents(consulta)
        resultados_bm25 = bm25_retriever.invoke(consulta)
        for i, doc in enumerate(resultados_bm25, 1):
            print(f"[{i}] {doc.metadata.get('source')}")

        # 🟢 3. HÍBRIDO
        print("\n--- RESULTADOS HÍBRIDOS ---")
        resultados = retriever.invoke(consulta)[:4]
        for i, doc in enumerate(resultados, 1):
            fuente = doc.metadata.get("source", "desconocida")
            fragmento = doc.page_content[:120].replace("\n", " ")
            print(f"[{i}] {fuente}")
            print(f"     {fragmento}...")