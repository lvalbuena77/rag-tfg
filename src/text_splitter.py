"""
Este módulo se encarga de dividir los documentos en fragmentos más pequeños utilizando la clase RecursiveCharacterTextSplitter de LangChain.
Esto es útil para manejar documentos grandes y mejorar la eficiencia en tareas de procesamiento de lenguaje natural.
Funciones:
- split_documents(documents): Toma una lista de documentos y devuelve una lista de fragmentos generados a partir de esos documentos.

"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents): # Toma una lista de documentos y devuelve una lista de fragmentos generados a partir de esos documentos.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Tamaño del chunk en caracteres
        chunk_overlap=150  # Cantidad de caracteres que se superponen entre chunks para mantener contexto
    )

    chunks = splitter.split_documents(documents) # Utiliza el splitter para dividir los documentos en fragmentos
    return chunks


if __name__ == "__main__": # Prueba la función de división de documentos
    from loaders import load_documents

    docs = load_documents("data/documents") # Carga los documentos desde el directorio especificado
    chunks = split_documents(docs) # Divide los documentos cargados en fragmentos utilizando la función split_documents

    print(f"Chunks generados: {len(chunks)}")    