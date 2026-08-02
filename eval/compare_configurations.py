"""
Script de comparativa de configuraciones del sistema RAG.

Ejecuta la evaluación RAGAS sobre múltiples configuraciones y genera
una tabla comparativa con los resultados. Compara:

  1. Tamaño de chunk  : 512 / 1000 / 2000 caracteres
  2. Top-k recuperado : 2 / 4 / 6 fragmentos
  3. Modelo LLM       : llama3.1 vs llama3.2:1b

Cada experimento de tamaño de chunk genera su propio índice vectorial
en un directorio temporal y lo elimina al finalizar.
Los experimentos de top-k y modelo reutilizan el índice existente.

Uso:
    # Comparativa completa (lenta, puede tardar horas en CPU)
    python eval/compare_configurations.py --all

    # Solo comparativa de top-k (rápida, reutiliza índice existente)
    python eval/compare_configurations.py --topk

    # Solo comparativa de modelos LLM
    python eval/compare_configurations.py --models

    # Solo comparativa de tamaños de chunk (requiere re-indexar)
    python eval/compare_configurations.py --chunks
"""

import sys
import os
import json
import shutil
import argparse
import datetime
import warnings
import pandas as pd

os.environ["RAGAS_DO_NOT_TRACK"] = "true"  # deshabilitar telemetría (evita bloqueos HTTP)

warnings.filterwarnings("ignore", category=DeprecationWarning, module="ragas")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from openai import OpenAI
from ragas.llms import llm_factory
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_huggingface import HuggingFaceEmbeddings as LCHFEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_chain import RAGChain
from loaders import load_documents
from vector_store import VectorStoreManager


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset_evaluacion.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "resultados")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "documents")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Configuraciones a comparar
CHUNK_SIZES = [512, 1000, 2000]        # caracteres (≈ 128, 256, 512 tokens)
CHUNK_OVERLAPS = [50, 150, 200]        # solapamiento proporcional al tamaño
TOP_K_VALUES = [2, 4, 6]
MODELS = ["llama3.1", "llama3.2:1b"]  # modelo grande vs modelo pequeño
DEFAULT_MODEL = "llama3.1"
DEFAULT_K = 4
DEFAULT_CHUNK_SIZE = 1000


# ---------------------------------------------------------------------------
# Helpers reutilizables
# ---------------------------------------------------------------------------

def cargar_dataset(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def construir_ragas_llm(model: str):
    """Crea un InstructorLLM usando la API OpenAI-compatible del servidor Ollama local."""
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    return llm_factory(model, provider="openai", client=client)


def construir_ragas_embeddings():
    return LangchainEmbeddingsWrapper(LCHFEmbeddings(model_name=EMBEDDING_MODEL))


def ejecutar_pipeline_sobre_dataset(
    dataset: list[dict],
    model: str,
    k: int,
    chroma_dir: str,
) -> Dataset:
    """
    Ejecuta el pipeline RAG sobre todas las preguntas del dataset.
    Devuelve un Dataset de HuggingFace con question/answer/contexts/ground_truth.
    """
    rag = RAGChain(
        model=model,
        persist_directory=chroma_dir,
        k=k,
        vector_weight=0.6,
        bm25_weight=0.4,
        temperature=0.0,
    )

    preguntas, respuestas, contextos, referencias = [], [], [], []
    total = len(dataset)

    for i, entrada in enumerate(dataset, start=1):
        pregunta = entrada["pregunta"]
        print(f"    [{i:02d}/{total}] {pregunta[:65]}...")
        resultado = rag.ask_with_sources(pregunta)
        preguntas.append(pregunta)
        respuestas.append(resultado["answer"])
        contextos.append([doc.page_content for doc in resultado["source_documents"]])
        referencias.append(entrada["respuesta_referencia"])

    return Dataset.from_dict({
        "question": preguntas,
        "answer": respuestas,
        "contexts": contextos,
        "ground_truth": referencias,
    })


def evaluar_con_ragas(hf_dataset: Dataset, ragas_llm, ragas_embeddings) -> dict:
    """Ejecuta RAGAS y devuelve un dict con las métricas medias."""
    metricas = [Faithfulness(), AnswerRelevancy(), ContextPrecision(), ContextRecall()]
    resultado = evaluate(
        dataset=hf_dataset,
        metrics=metricas,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
    )
    df = resultado.to_pandas()
    cols_excluir = {"question", "answer", "contexts", "ground_truth"}
    cols_metricas = [c for c in df.columns if c not in cols_excluir and df[c].dtype != object]
    return {col: round(df[col].mean(), 4) for col in cols_metricas}


def reindexar_corpus(chunk_size: int, chunk_overlap: int, chroma_dir: str) -> None:
    """
    Re-indexa el corpus con el tamaño de chunk indicado en un directorio
    ChromaDB temporal. El directorio se crea desde cero.
    """
    print(f"    Re-indexando corpus con chunk_size={chunk_size}, overlap={chunk_overlap}...")
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)

    docs = load_documents(DOCS_DIR)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    print(f"    Chunks generados: {len(chunks)}")

    store_manager = VectorStoreManager(persist_directory=chroma_dir)
    store_manager.create_vector_store(chunks)
    print(f"    Índice creado en: {chroma_dir}")


def guardar_tabla_comparativa(filas: list[dict], nombre_fichero: str) -> None:
    """Guarda y muestra la tabla comparativa."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, nombre_fichero)
    df = pd.DataFrame(filas)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print("\n" + "=" * 70)
    print(df.to_string(index=False))
    print("=" * 70)
    print(f"\nTabla guardada en: {output_path}")
    return df


# ---------------------------------------------------------------------------
# Experimento 1: comparativa de top-k
# ---------------------------------------------------------------------------

def comparativa_topk(dataset: list[dict], ragas_llm, ragas_embeddings) -> None:
    print("\n" + "=" * 70)
    print("EXPERIMENTO 1 — Comparativa de top-k")
    print(f"  Modelo: {DEFAULT_MODEL} | Chunk size: {DEFAULT_CHUNK_SIZE}")
    print("=" * 70)

    filas = []
    for k in TOP_K_VALUES:
        print(f"\n  top-k = {k}")
        hf_dataset = ejecutar_pipeline_sobre_dataset(
            dataset, model=DEFAULT_MODEL, k=k, chroma_dir=CHROMA_DIR
        )
        metricas = evaluar_con_ragas(hf_dataset, ragas_llm, ragas_embeddings)
        fila = {"configuracion": f"top_k={k}", "modelo": DEFAULT_MODEL, "top_k": k,
                "chunk_size": DEFAULT_CHUNK_SIZE, **metricas}
        filas.append(fila)
        print(f"    Resultados: {metricas}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    guardar_tabla_comparativa(filas, f"comparativa_topk_{timestamp}.csv")


# ---------------------------------------------------------------------------
# Experimento 2: comparativa de modelos LLM
# ---------------------------------------------------------------------------

def comparativa_modelos(dataset: list[dict], ragas_embeddings, model_filter: list = None) -> None:
    print("\n" + "=" * 70)
    print("EXPERIMENTO 2 — Comparativa de modelos LLM")
    print(f"  Top-k: {DEFAULT_K} | Chunk size: {DEFAULT_CHUNK_SIZE}")
    print("=" * 70)

    modelos_a_ejecutar = [m for m in MODELS if model_filter is None or m in model_filter]
    filas = []
    for model in modelos_a_ejecutar:
        print(f"\n  Modelo: {model}")
        # Cada modelo necesita su propio ragas_llm
        ragas_llm = construir_ragas_llm(model)
        ragas_embeddings_local = construir_ragas_embeddings()

        hf_dataset = ejecutar_pipeline_sobre_dataset(
            dataset, model=model, k=DEFAULT_K, chroma_dir=CHROMA_DIR
        )
        metricas = evaluar_con_ragas(hf_dataset, ragas_llm, ragas_embeddings_local)
        fila = {"configuracion": f"model={model}", "modelo": model, "top_k": DEFAULT_K,
                "chunk_size": DEFAULT_CHUNK_SIZE, **metricas}
        filas.append(fila)
        print(f"    Resultados: {metricas}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    guardar_tabla_comparativa(filas, f"comparativa_modelos_{timestamp}.csv")


# ---------------------------------------------------------------------------
# Experimento 3: comparativa de tamaños de chunk
# ---------------------------------------------------------------------------

def comparativa_chunks(dataset: list[dict], ragas_llm, ragas_embeddings) -> None:
    print("\n" + "=" * 70)
    print("EXPERIMENTO 3 — Comparativa de tamaños de chunk")
    print(f"  Modelo: {DEFAULT_MODEL} | Top-k: {DEFAULT_K}")
    print("  ADVERTENCIA: este experimento re-indexa el corpus para cada")
    print("  tamaño. Al finalizar se restaura el índice con chunk_size=1000.")
    print("=" * 70)

    filas = []
    chroma_tmp_base = os.path.join(os.path.dirname(__file__), "..", "chroma_db_tmp")

    for chunk_size, overlap in zip(CHUNK_SIZES, CHUNK_OVERLAPS):
        chroma_tmp = f"{chroma_tmp_base}_{chunk_size}"
        print(f"\n  chunk_size = {chunk_size} (overlap={overlap})")

        try:
            reindexar_corpus(chunk_size, overlap, chroma_tmp)
            hf_dataset = ejecutar_pipeline_sobre_dataset(
                dataset, model=DEFAULT_MODEL, k=DEFAULT_K, chroma_dir=chroma_tmp
            )
            metricas = evaluar_con_ragas(hf_dataset, ragas_llm, ragas_embeddings)
            fila = {"configuracion": f"chunk={chunk_size}", "modelo": DEFAULT_MODEL,
                    "top_k": DEFAULT_K, "chunk_size": chunk_size, **metricas}
            filas.append(fila)
            print(f"    Resultados: {metricas}")
        finally:
            if os.path.exists(chroma_tmp):
                shutil.rmtree(chroma_tmp)
                print(f"    Índice temporal eliminado: {chroma_tmp}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    guardar_tabla_comparativa(filas, f"comparativa_chunks_{timestamp}.csv")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Comparativa de configuraciones del sistema RAG"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Ejecutar los tres experimentos")
    group.add_argument("--topk", action="store_true", help="Solo comparativa de top-k")
    group.add_argument("--models", action="store_true", help="Solo comparativa de modelos LLM")
    group.add_argument("--chunks", action="store_true", help="Solo comparativa de chunk sizes")
    parser.add_argument(
        "--limit", type=int, default=None, metavar="N",
        help="Usar solo las primeras N preguntas del dataset (útil para pruebas rápidas)"
    )
    parser.add_argument(
        "--model-filter", nargs="+", metavar="MODEL",
        help="Ejecutar solo los modelos indicados en la comparativa de modelos (e.g. --model-filter llama3.2:1b)"
    )
    args = parser.parse_args()

    print("Cargando dataset de evaluación...")
    dataset = cargar_dataset(DATASET_PATH)
    total_disponible = len(dataset)
    if args.limit:
        dataset = dataset[:args.limit]
        print(f"  Modo reducido: usando {args.limit} de {total_disponible} preguntas.")
    else:
        print(f"  {len(dataset)} preguntas cargadas.")

    print("Inicializando modelos RAGAS locales...")
    ragas_llm = construir_ragas_llm(DEFAULT_MODEL)
    ragas_embeddings = construir_ragas_embeddings()

    if args.all or args.topk:
        comparativa_topk(dataset, ragas_llm, ragas_embeddings)

    if args.all or args.models:
        comparativa_modelos(dataset, ragas_embeddings, model_filter=args.model_filter)

    if args.all or args.chunks:
        comparativa_chunks(dataset, ragas_llm, ragas_embeddings)

    print("\nComparativa completada.")


if __name__ == "__main__":
    main()
