import os
from text_generation import Client


def main():
    client = Client("http://0.0.0.0:8000")
    input_text = "Tell me a joke."
    response = client.generate(input_text, max_new_tokens=50)
    print("Generated Text:", response.generated_text)

if __name__ == "__main__":
    main()