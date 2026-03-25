"""
Este módulo se encarga de dividir los documentos en fragmentos más pequeños utilizando la clase RecursiveCharacterTextSplitter de LangChain.
Esto es útil para manejar documentos grandes y mejorar la eficiencia en tareas de procesamiento de lenguaje natural.
Funciones:
- split_documents(documents): Toma una lista de documentos y devuelve una lista de fragmentos generados a partir de esos documentos.

"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Tamaño del chunk en caracteres
        chunk_overlap=150  # Cantidad de caracteres que se superponen entre chunks para mantener contexto
    )

    chunks = splitter.split_documents(documents)
    return chunks


if __name__ == "__main__":
    from loaders import load_documents

    docs = load_documents("data/documents")
    chunks = split_documents(docs)

    print(f"Chunks generados: {len(chunks)}")