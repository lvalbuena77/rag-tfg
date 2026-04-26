"""
Módulo principal del pipeline RAG (Retrieval-Augmented Generation).

Integra el módulo de recuperación híbrida (RetrieverManager) con el modelo
de lenguaje local llama3.1 ejecutado mediante Ollama, construyendo una cadena
de generación anclada al contexto recuperado (grounding).

El sistema prompt de anclaje obliga al modelo a responder exclusivamente
a partir de los fragmentos recuperados del corpus, evitando la generación
de información no fundamentada (alucinaciones).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from retriever import RetrieverManager


# ---------------------------------------------------------------------------
# Prompt de anclaje (grounding prompt)
# ---------------------------------------------------------------------------
# El system prompt instruye al modelo a responder SOLO con la información
# contenida en el contexto recuperado, sin inventar datos externos.
# Si la respuesta no está en el contexto, el modelo debe indicarlo.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Eres un asistente técnico especializado en la documentación interna de una organización de desarrollo de software.

Tu tarea es responder preguntas utilizando únicamente la información contenida en los fragmentos de documentación que se proporcionan a continuación.

INSTRUCCIONES:
1. Basa tu respuesta en el contenido de los fragmentos proporcionados. Si la información está en el contexto, extráela y preséntala de forma clara y estructurada.
2. Cita el documento de origen cuando sea útil para el usuario (por ejemplo: "Según el manual de incorporación...").
3. Solo si la información requerida NO aparece en ninguno de los fragmentos, indica: "No encuentro información suficiente en la documentación disponible para responder a esta pregunta."
4. No inventes datos, fechas, nombres, versiones ni procedimientos que no aparezcan en el contexto.
5. Responde en el mismo idioma en que se formula la pregunta.

FRAGMENTOS DE DOCUMENTACIÓN:
{context}"""

HUMAN_PROMPT = "{question}"


def format_docs(docs: list[Document]) -> str:
    """
    Formatea una lista de documentos recuperados en un único bloque de texto.

    Cada fragmento se separa visualmente e incluye el nombre del documento
    de origen para facilitar la trazabilidad de la respuesta.

    :param docs: lista de objetos Document recuperados por el retriever
    :return: cadena de texto con todos los fragmentos formateados
    """
    formatted = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "desconocido")
        source_name = os.path.basename(source)
        formatted.append(
            f"[Fragmento {i} - Fuente: {source_name}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)


class RAGChain:
    """
    Cadena RAG completa: recuperación híbrida + generación con LLM local.

    Combina RetrieverManager (búsqueda vectorial + BM25) con ChatOllama
    (llama3.1) para generar respuestas fundamentadas en el corpus documental.
    """

    def __init__(
        self,
        model: str = "llama3.1",
        persist_directory: str = "chroma_db",
        k: int = 4,
        vector_weight: float = 0.6, # Ajusta el peso de la búsqueda vectorial (0.0 - 1.0)
        bm25_weight: float = 0.4, # Ajusta el peso de cada método de recuperación (vectorial vs BM25)
        temperature: float = 0.0, # Respuestas más deterministas y ancladas al contexto con temperatura baja
    ):
        """
        Inicializa la cadena RAG.

        :param model: nombre del modelo Ollama a utilizar
        :param persist_directory: ruta de la base de datos vectorial ChromaDB
        :param k: número de fragmentos a recuperar por cada retriever
        :param vector_weight: peso de la búsqueda vectorial (0.0 - 1.0)
        :param bm25_weight: peso de la búsqueda léxica BM25 (0.0 - 1.0)
        :param temperature: temperatura del modelo (0.0 = respuestas deterministas)
        """
        self.model = model
        self.persist_directory = persist_directory
        self.k = k
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.temperature = temperature

        self._chain = None  # La cadena se construye de forma perezosa (lazy)
        self._retriever = None  # Reutilizado en ask_with_sources para evitar doble carga

    def _build_chain(self):
        """
        Construye la cadena LCEL (LangChain Expression Language):
        retriever → format_docs → prompt → llm → output_parser
        """
        # Recuperador híbrido (se construye una sola vez y se reutiliza)
        retriever_manager = RetrieverManager(
            persist_directory=self.persist_directory,
            k=self.k,
            vector_weight=self.vector_weight,
            bm25_weight=self.bm25_weight,
        )
        self._retriever = retriever_manager.get_retriever()
        retriever = self._retriever

        # Modelo de lenguaje local (Ollama)
        llm = ChatOllama(
            model=self.model,
            temperature=self.temperature,  # 0.0 → respuestas más consistentes y ancladas al contexto
        )

        # Plantilla de prompt con system prompt de anclaje
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ])

        # Cadena LCEL completa
        chain = (
            {
                "context": retriever | format_docs,  # Recupera fragmentos y los formatea
                "question": RunnablePassthrough(),    # Pasa la pregunta sin modificar
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        return chain

    def ask(self, question: str) -> str:
        """
        Realiza una consulta al sistema RAG y devuelve la respuesta generada.

        :param question: pregunta en lenguaje natural
        :return: respuesta generada por el LLM, anclada al contexto recuperado
        """
        if self._chain is None:
            self._chain = self._build_chain()

        return self._chain.invoke(question)

    def ask_with_sources(self, question: str) -> dict:
        """
        Realiza una consulta y devuelve la respuesta junto con los fragmentos
        recuperados del corpus (para depuración y evaluación).

        :param question: pregunta en lenguaje natural
        :return: diccionario con 'answer' y 'source_documents'
        """
        # Generar respuesta (construye la cadena y el retriever si aún no existen)
        answer = self.ask(question)

        # Reutilizar el retriever ya construido para obtener los documentos fuente
        docs = self._retriever.invoke(question)

        return {
            "answer": answer,
            "source_documents": docs,
        }


# ---------------------------------------------------------------------------
# Bloque de prueba
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Seleccionar modelo: comentar el que no se quiera usar
    modelo = "llama3.1"         # Modelo completo — para capturas finales (~4.7 GB, lento en CPU)
    # modelo = "llama3.2:1b"    # Modelo ligero — para pruebas de desarrollo (~770 MB, rápido)

    print("=" * 70)
    print("SISTEMA RAG - PRUEBA DE FUNCIONAMIENTO")
    print(f"Modelo: {modelo} | Ollama local")
    print("=" * 70)

    rag = RAGChain(
        model=modelo,
        k=4,
        vector_weight=0.6,
        bm25_weight=0.4,
        temperature=0.0,
    )

    test_queries = [
        "¿Cómo se incorpora un nuevo miembro al equipo?",
        "¿Cuáles son las buenas prácticas de desarrollo de software?",
        "¿Qué microservicios componen la arquitectura del sistema?",
        "¿Cuáles son las políticas de seguridad de la plataforma?",
    ]

    for query in test_queries:
        print(f"\n{'─' * 70}")
        print(f"PREGUNTA: {query}")
        print("─" * 70)

        result = rag.ask_with_sources(query)

        print(f"\nRESPUESTA:\n{result['answer']}")

        print(f"\nFUENTES UTILIZADAS ({len(result['source_documents'])} fragmentos):")
        seen = set()
        for doc in result["source_documents"]:
            source = os.path.basename(doc.metadata.get("source", "desconocido"))
            if source not in seen:
                print(f"  - {source}")
                seen.add(source)
