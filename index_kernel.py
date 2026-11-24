
import os
import hashlib
from pathlib import Path

import chromadb
import ollama

KERNEL_ROOT = Path.home() / "embedded-ai/linux"
DB_PATH = "./kernel_db"

ROOTS = [
    "drivers/net/wireless",
    "drivers/tty",
    "drivers/gpio",
    "arch/arm64",
    "kernel",
    "mm",
    "include/linux",
]

EXTENSIONS = {
    ".c", ".h", ".S", ".s", ".dts",
    ".dtsi", ".txt", ".rst"
}

SPECIAL_FILES = {"Makefile", "Kconfig"}

EXCLUDED = {
    ".git", "build", "out",
    "__pycache__", "node_modules"
}

CHUNK_SIZE = 80
OVERLAP = 15
BATCH_SIZE = 16


def scan_files():
    for root in ROOTS:
        directory = KERNEL_ROOT / root

        if not directory.exists():
            print("Skipping:", directory)
            continue

        for current, dirs, files in os.walk(directory):
            dirs[:] = [
                d for d in dirs if d not in EXCLUDED
            ]

            for filename in files:
                path = Path(current) / filename

                if not (
                    path.suffix in EXTENSIONS
                    or filename in SPECIAL_FILES
                ):
                    continue

                try:
                    if path.stat().st_size > 500_000:
                        continue
                    yield path
                except OSError:
                    continue


def split_chunks(content):
    lines = content.splitlines()
    step = CHUNK_SIZE - OVERLAP

    for start in range(0, len(lines), step):
        end = min(start + CHUNK_SIZE, len(lines))
        chunk = "\n".join(lines[start:end])

        if chunk.strip():
            yield start + 1, end, chunk


def save_batch(collection, documents, ids, metadata):
    response = ollama.embed(
        model="nomic-embed-text",
        input=documents
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=response["embeddings"],
        metadatas=metadata
    )


def main():
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name="linux_kernel"
    )

    docs, ids, metadata = [], [], []
    total = 0

    for path in scan_files():
        try:
            content = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except OSError:
            continue

        relative = str(path.relative_to(KERNEL_ROOT))

        for start, end, chunk in split_chunks(content):
            chunk_id = hashlib.sha256(
                f"{relative}:{start}:{end}".encode()
            ).hexdigest()

            docs.append(chunk)
            ids.append(chunk_id)

            metadata.append({
                "file": relative,
                "start_line": start,
                "end_line": end
            })

            if len(docs) >= BATCH_SIZE:
                save_batch(collection, docs, ids, metadata)
                total += len(docs)
                print("Indexed chunks:", total)

                docs, ids, metadata = [], [], []

    if docs:
        save_batch(collection, docs, ids, metadata)
        total += len(docs)

    print("\nIndexing complete!")
    print("Total chunks:", total)
    print("Database:", DB_PATH)


if __name__ == "__main__":
    main()
