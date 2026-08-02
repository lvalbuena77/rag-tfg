"""
Script de evaluación del sistema RAG con el framework RAGAS.

Ejecuta las cuatro métricas principales sobre el dataset de evaluación:
  - faithfulness        : ¿está la respuesta anclada en el contexto recuperado?
  - answer_relevancy    : ¿responde la respuesta a la pregunta formulada?
  - context_precision   : ¿son los fragmentos recuperados relevantes para la pregunta?
  - context_recall      : ¿cubre el contexto recuperado la respuesta de referencia?

Todos los modelos (LLM y embeddings) se ejecutan en local mediante Ollama
y sentence-transformers, sin enviar datos a servicios externos.

Uso:
    python eval/evaluate_ragas.py
    python eval/evaluate_ragas.py --model llama3.2:1b
    python eval/evaluate_ragas.py --k 6 --output eval/resultados/resultados_k6.csv
"""

import sys
import os
import json
import argparse
import datetime
import pandas as pd

os.environ["RAGAS_DO_NOT_TRACK"] = "true"  # deshabilitar telemetría (evita bloqueos HTTP)

# Añadir src/ al path para importar los módulos del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datasets import Dataset
from ragas import evaluate
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="ragas")

from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from openai import OpenAI
from ragas.llms import llm_factory
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_huggingface import HuggingFaceEmbeddings as LCHFEmbeddings

from rag_chain import RAGChain


# ---------------------------------------------------------------------------
# Configuración por defecto
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "llama3.1"
DEFAULT_K = 4
DEFAULT_DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset_evaluacion.json")
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "resultados")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def cargar_dataset(path: str) -> list[dict]:
    """Carga el dataset de evaluación desde el fichero JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def construir_ragas_llm(model: str):
    """Crea un InstructorLLM usando la API OpenAI-compatible del servidor Ollama local."""
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    return llm_factory(model, provider="openai", client=client)


def construir_ragas_embeddings():
    """Instancia embeddings locales compatibles con las métricas nuevas de RAGAS."""
    return LangchainEmbeddingsWrapper(LCHFEmbeddings(model_name=EMBEDDING_MODEL))


def construir_metricas() -> list:
    """Instancia las cuatro métricas RAGAS; el LLM se inyecta en evaluate()."""
    return [Faithfulness(), AnswerRelevancy(), ContextPrecision(), ContextRecall()]


def ejecutar_pipeline(dataset: list[dict], model: str, k: int) -> dict:
    """
    Ejecuta el pipeline RAG sobre cada pregunta del dataset.

    Para cada entrada obtiene:
      - answer    : respuesta generada por el LLM
      - contexts  : lista de fragmentos recuperados (texto plano)

    Devuelve un diccionario con listas paralelas listas para construir
    un Dataset de HuggingFace.
    """
    rag = RAGChain(
        model=model,
        persist_directory=CHROMA_DIR,
        k=k,
        vector_weight=0.6,
        bm25_weight=0.4,
        temperature=0.0,
    )

    preguntas = []
    respuestas_generadas = []
    contextos_recuperados = []
    respuestas_referencia = []

    total = len(dataset)
    for i, entrada in enumerate(dataset, start=1):
        pregunta = entrada["pregunta"]
        referencia = entrada["respuesta_referencia"]

        print(f"  [{i:02d}/{total}] Procesando: {pregunta[:70]}...")

        resultado = rag.ask_with_sources(pregunta)
        answer = resultado["answer"]
        contexts = [doc.page_content for doc in resultado["source_documents"]]

        preguntas.append(pregunta)
        respuestas_generadas.append(answer)
        contextos_recuperados.append(contexts)
        respuestas_referencia.append(referencia)

    return {
        "question": preguntas,
        "answer": respuestas_generadas,
        "contexts": contextos_recuperados,
        "ground_truth": respuestas_referencia,
    }


def guardar_resultados(result_df: pd.DataFrame, output_path: str, config: dict) -> None:
    """Guarda el DataFrame de resultados en CSV y muestra un resumen por consola."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nResultados guardados en: {output_path}")

    # Resumen de métricas (medias) — columnas dinámicas para robustez
    cols_excluir = {"modelo", "top_k", "question", "answer", "contexts", "ground_truth"}
    metricas_disponibles = [c for c in result_df.columns if c not in cols_excluir and result_df[c].dtype != object]

    print("\n" + "=" * 60)
    print("RESUMEN — Métricas medias del sistema")
    print(f"  Modelo LLM : {config['model']}")
    print(f"  Top-k      : {config['k']}")
    print("-" * 60)
    for metrica in metricas_disponibles:
        media = result_df[metrica].mean()
        print(f"  {metrica:<25} {media:.4f}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evaluación del sistema RAG con RAGAS (modelos locales)"
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Modelo Ollama a evaluar (por defecto: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--k", type=int, default=DEFAULT_K,
        help=f"Número de fragmentos a recuperar por consulta (por defecto: {DEFAULT_K})"
    )
    parser.add_argument(
        "--dataset", default=DEFAULT_DATASET_PATH,
        help="Ruta al fichero JSON del dataset de evaluación"
    )
    parser.add_argument(
        "--output", default=None,
        help="Ruta del CSV de salida (se genera automáticamente si no se indica)"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limita el número de preguntas a evaluar (útil para pruebas rápidas)"
    )
    args = parser.parse_args()

    # Nombre de fichero de salida automático si no se especifica
    if args.output is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"ragas_{args.model.replace(':', '_')}_k{args.k}_{timestamp}.csv"
        args.output = os.path.join(DEFAULT_OUTPUT_DIR, nombre)

    config = {"model": args.model, "k": args.k}

    print("=" * 60)
    print("EVALUACIÓN RAGAS — Sistema RAG (modelos locales)")
    print(f"  Modelo LLM  : {args.model}")
    print(f"  Top-k       : {args.k}")
    print(f"  Dataset     : {args.dataset}")
    print(f"  Embeddings  : {EMBEDDING_MODEL}")
    print("=" * 60)

    # 1. Cargar dataset
    print("\n[1/4] Cargando dataset de evaluación...")
    dataset_raw = cargar_dataset(args.dataset)
    total_disponible = len(dataset_raw)
    if args.limit:
        dataset_raw = dataset_raw[:args.limit]
        print(f"      Modo prueba: usando {args.limit} de {total_disponible} preguntas.")
    print(f"      {len(dataset_raw)} preguntas cargadas.")

    # 2. Ejecutar pipeline RAG sobre todas las preguntas
    print("\n[2/4] Ejecutando pipeline RAG...")
    datos = ejecutar_pipeline(dataset_raw, model=args.model, k=args.k)

    # 3. Construir Dataset de HuggingFace y configurar RAGAS con modelos locales
    print("\n[3/4] Configurando RAGAS con modelos locales...")
    hf_dataset = Dataset.from_dict(datos)

    ragas_llm = construir_ragas_llm(args.model)
    ragas_embeddings = construir_ragas_embeddings()
    metricas = construir_metricas()

    # 4. Evaluar con RAGAS
    print("\n[4/4] Ejecutando evaluación RAGAS (puede tardar varios minutos)...")
    resultado = evaluate(
        dataset=hf_dataset,
        metrics=metricas,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
    )

    # Convertir a DataFrame y añadir columnas de configuración
    result_df = resultado.to_pandas()
    result_df.insert(0, "modelo", args.model)
    result_df.insert(1, "top_k", args.k)

    # Guardar y mostrar resumen
    guardar_resultados(result_df, args.output, config)


if __name__ == "__main__":
    main()
