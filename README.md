# Sistema RAG Local para Gestión de Conocimiento Corporativo

## Trabajo Fin de Grado – Ingeniería Informática

Autor: Luis Valbuena Arribas  
Tutor: Cuauhtémoc Ocampo Herrera  

---
# Licencia

Proyecto desarrollado con fines académicos como parte del Trabajo Fin de Grado en Ingeniería Informática.

# 1. Descripción del proyecto

Este proyecto consiste en el diseño e implementación de un sistema **RAG (Retrieval-Augmented Generation)** ejecutado completamente en local, que permite consultar documentación corporativa mediante lenguaje natural.

El sistema permite a un usuario realizar preguntas sobre un conjunto de documentos internos (PDF, Word, Markdown) y obtener respuestas generadas por un modelo de lenguaje que utiliza únicamente la información contenida en dichos documentos.

El objetivo es simular un sistema de gestión del conocimiento corporativo que respete la privacidad de los datos y no dependa de servicios en la nube.

---

# 2. Problema que se pretende resolver

Las empresas manejan grandes volúmenes de documentación interna como:

- manuales técnicos
- documentación de APIs
- guías de instalación
- políticas internas
- documentación de proyectos

Las búsquedas tradicionales por palabras clave tienen limitaciones para recuperar información relevante cuando el usuario formula preguntas en lenguaje natural.

Además, muchas organizaciones no pueden utilizar modelos de lenguaje en la nube por motivos de:

- privacidad
- seguridad
- cumplimiento normativo
- control de datos

Por ello, este proyecto propone un sistema RAG ejecutado completamente en local.

---

# 3. Arquitectura del sistema

El sistema seguirá una arquitectura RAG compuesta por las siguientes fases:

1. **Ingesta de documentos**
2. **Procesamiento y fragmentación (chunking)**
3. **Generación de embeddings**
4. **Almacenamiento en base de datos vectorial**
5. **Recuperación híbrida de información**
6. **Generación de respuestas mediante LLM**

Pipeline del sistema:

Documentos (PDF, Word, Markdown)
        ↓
Carga de documentos
        ↓
Text Splitter
        ↓
Embeddings
        ↓
Vector Database
        ↓
Hybrid Retriever
        ↓
LLM (Ollama)
        ↓
Respuesta generada

---

# 4. Tecnologías utilizadas

El sistema se implementará utilizando las siguientes tecnologías:

Lenguaje de programación:

- Python 3

Frameworks y librerías:

- LangChain
- ChromaDB
- RAGAS
- rank-bm25
- sentence-transformers

Modelo de lenguaje:

- Llama 3
- Mistral

Ejecución local de modelos:

- Ollama

Interfaz de usuario:

- Streamlit

Entorno de desarrollo:

- Visual Studio Code
- Git
- Python venv

---

# 5. Procesamiento de documentos

Los documentos se procesarán utilizando un **Recursive Character Text Splitter** con solapamiento (overlap) del 10–15%.

Esto permite evitar la pérdida de contexto cuando un párrafo se divide en fragmentos.

Ejemplo de configuración:
chunk_size = 1000
chunk_overlap = 150


---

# 6. Búsqueda híbrida

El sistema implementará una estrategia de **búsqueda híbrida** que combina:

- búsqueda semántica (vectorial)
- búsqueda tradicional por palabras clave (BM25)

Esto mejora la recuperación de información cuando se utilizan:

- nombres propios
- identificadores técnicos
- términos específicos

---

# 7. Grounding del modelo

El sistema utilizará un **System Prompt de anclaje** para obligar al modelo a responder únicamente utilizando la información contenida en los documentos.

Ejemplo:

Responde únicamente utilizando la información proporcionada
en los documentos. Si la respuesta no se encuentra en los
documentos, indica que no se dispone de esa información.


Esto evita que el modelo genere información inventada.

---

# 8. Evaluación del sistema

La evaluación del sistema se realizará utilizando el framework **RAGAS**, que permite medir métricas como:

- precisión
- relevancia de la recuperación
- fidelidad de la respuesta

Esto permitirá obtener una evaluación cuantitativa del sistema.

---

# 9. Estructura del proyecto

rag-tfg/
│
├── data/
│ └── documents/
│
├── src/
│ ├── loaders.py
│ ├── text_splitter.py
│ ├── embeddings.py
│ ├── vector_store.py
│ ├── retriever.py
│ ├── rag_pipeline.py
│ └── app.py
│
├── evaluation/
│ └── ragas_eval.py
│
├── requirements.txt
│
└── README.md


---

# 10. Estado actual del proyecto

- Preparación del entorno de desarrollo
- Instalación de dependencias
- Diseño de la arquitectura del sistema
- Preparación del corpus documental

- Entorno de desarrollo configurado
- Corpus documental generado (Markdown, PDF, DOCX)
- Módulo de carga de documentos implementado
- Módulo de fragmentación (text splitting) implementado
- Pruebas iniciales del pipeline de ingesta completadas
---

# 11. Próximos pasos

1. Preparar los documentos de prueba
2. Implementar el módulo de carga de documentos
3. Implementar el sistema de fragmentación de texto
4. Generar embeddings
5. Configurar la base de datos vectorial
6. Implementar el pipeline RAG
7. Desarrollar la interfaz de usuario
8. Evaluar el sistema

9. Implementar generación de embeddings
10. Configurar base de datos vectorial (ChromaDB)
11. Implementar sistema de recuperación
12. Integrar LLM mediante Ollama
13. Construir pipeline RAG completo
14. Desarrollar interfaz con Streamlit
15. Evaluar sistema con RAGAS


# 12. Instalación y ejecución del proyecto

Clonar el repositorio:

git clone https://github.com/usuario/rag-tfg.git
cd rag-tfg

Crear entorno virtual:
python -m venv venv

Activar entorno virtual:

Windows:
venv\Scripts\activate

Instalar dependencias:
pip install -r requirements.txt

Ejecutar aplicación:
streamlit run src/app.py

