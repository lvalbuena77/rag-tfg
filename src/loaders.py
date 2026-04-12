"""
Este módulo contiene funciones para cargar documentos desde un directorio específico. 
Soporta archivos PDF, DOCX y Markdown. Utiliza la biblioteca LangChain para manejar la carga de documentos.
Funciones:
- load_documents(directory_path): Carga documentos desde el directorio especificado y devuelve una lista de documentos.

"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
import os
import logging
logging.getLogger("pypdf").setLevel(logging.ERROR)


def load_documents(directory_path): # Carga documentos desde un directorio específico y devuelve una lista de documentos.
    documents = []

    for filename in os.listdir(directory_path): # Itera sobre los archivos en el directorio especificado
        filepath = os.path.join(directory_path, filename)

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            documents.extend(loader.load())

        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(filepath)
            documents.extend(loader.load())

        elif filename.endswith(".md"):
            loader = TextLoader(filepath, encoding="utf-8")
            documents.extend(loader.load())

    return documents


if __name__ == "__main__": # Prueba la función de carga de documentos
    docs = load_documents("data/documents")
    print(f"Documentos cargados: {len(docs)}")