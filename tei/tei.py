import os
from text_embeddings import Client

def main():
    client = Client("http://0.0.0.0:8080")
    input_texts = ["Tell me a joke."]
    response = client.embed(input_texts)
    print("Embedding vector:", response.embeddings[0])

if __name__ == "__main__":
    main()
