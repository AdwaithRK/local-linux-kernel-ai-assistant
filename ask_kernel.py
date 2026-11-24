
import chromadb
import ollama

# Connect to existing vector database
client = chromadb.PersistentClient(
    path="./kernel_db"
)

collection = client.get_collection(
    name="linux_kernel"
)

print("Linux Kernel Assistant Ready!")
print("Indexed chunks:", collection.count())


def ask(question):

    print("\n[1/3] Generating question embedding...", flush=True)
    # 1. Convert question into embedding
    embedding = ollama.embed(
        model="nomic-embed-text",
        input=question
    )

    
    print("[2/3] Searching ChromaDB...", flush=True)
    # 2. Retrieve relevant source code
    results = collection.query(
        query_embeddings=embedding["embeddings"],
        n_results=5
    )
    
    print("[3/3] Sending context to Qwen3...", flush=True)
    # 3. Construct context
    context = ""

    for doc, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        context += f"""
SOURCE FILE: {metadata['file']}
LINES: {metadata['start_line']}-{metadata['end_line']}

{doc}

-----------------------------
"""

    # 4. Send retrieved context to Qwen
    prompt = f"""
You are an expert Linux kernel engineer.

Answer the question using the supplied Linux
kernel source code.

Explain:
- Relevant functions
- Data structures
- Execution flow
- Important relationships

Cite source files and line numbers.

If the provided source is insufficient,
clearly mention that.

SOURCE CODE:
{context}

QUESTION:
{question}
"""


    print("\nQwen is generating:\n", flush=True)

    stream = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        think=False,
        stream=True,
        options={
            "num_ctx": 8192,
            "num_predict": 512
        }
    )

    for chunk in stream:
        content = chunk["message"]["content"]
        print(content, end="", flush=True)

    print("\n\n[Done]")



    print("[Done] Answer generated!", flush=True)


    for metadata in results["metadatas"][0]:
        print(
            metadata["file"],
            metadata["start_line"],
            metadata["end_line"]
        )


while True:

    question = input("\nAsk your kernel assistant (q to quit): ")

    if question.lower() == "q":
        break

    ask(question)
