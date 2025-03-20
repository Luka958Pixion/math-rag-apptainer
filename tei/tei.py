import httpx


def embed_texts(base_url, input_texts):
    response = httpx.post(
        f"{base_url}/embed",
        json={"inputs": input_texts}
    )
    response.raise_for_status()
    return response.json()

def main():
    base_url = "http://0.0.0.0:8080"
    input_texts = ["Tell me a joke."]
    embeddings = embed_texts(base_url, input_texts)
    print("Embedding vector:", embeddings[0])

if __name__ == "__main__":
    main()
