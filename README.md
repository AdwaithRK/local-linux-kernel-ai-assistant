# Local Linux Kernel Assistant

An AI-powered assistant for exploring and understanding Linux kernel source code using **Retrieval-Augmented Generation (RAG)**.

The project runs locally using Ollama and combines a Large Language Model (LLM) with a vector database to provide context-aware answers based on actual Linux kernel source code.

## Architecture

The project uses the following components:

- **Qwen3 8B:** Large Language Model responsible for understanding questions and generating explanations.
- **Nomic Embed Text:** Embedding model that converts source-code chunks and user queries into numerical vectors.
- **ChromaDB:** Vector database that stores embeddings, source-code chunks, and metadata for semantic retrieval.
- **Ollama:** Local LLM runtime responsible for model execution and inference.
- **Python:** Connects the components and orchestrates the RAG pipeline.

## How It Works

The application consists of two main stages.

### 1. Indexing

The indexing pipeline prepares the Linux kernel source code for semantic search.

1. Scans selected Linux kernel source directories.
2. Splits source files into smaller overlapping chunks.
3. Generates embeddings using Nomic Embed Text.
4. Stores embeddings, original source code, and metadata in ChromaDB.

### 2. Question Answering

When a user asks a question:

1. Converts the question into an embedding using Nomic.
2. Searches ChromaDB for semantically relevant code chunks.
3. Retrieves the original source code and associated metadata.
4. Constructs a prompt containing the question and retrieved context.
5. Sends the prompt to Qwen3 through Ollama.
6. Streams the generated explanation to the user.

## Project Structure

```text
embedded-ai/
├── ask_kernel.py       # RAG question-answering application
├── index_kernel.py     # Source-code indexing pipeline
├── kernel_db/          # Persistent ChromaDB database
└── linux/              # Linux kernel source tree
```

## Technology Stack

- Python
- Ollama
- Qwen3 8B
- Nomic Embed Text
- ChromaDB
- Retrieval-Augmented Generation (RAG)

## Goals

- Build a locally running AI assistant for Linux kernel development.
- Explore LLM inference on resource-constrained hardware.
- Understand vector databases and semantic retrieval.
- Experiment with embedding models and quantized LLMs.
- Explore deployment on ARM64 embedded Linux platforms.
- Investigate GPU acceleration and edge AI inference.

## Future Improvements

- Hybrid retrieval (semantic search + keyword search).
- Function-aware source-code chunking.
- C/C++ symbol indexing.
- Call graph-based retrieval.
- Support for U-Boot and ARM Trusted Firmware (ATF).
- Deployment on ARM64 embedded boards.
- Hardware-accelerated inference.

## Motivation

The goal is to explore how locally running language models can assist embedded systems engineers in understanding, navigating, and debugging large codebases such as the Linux kernel.


