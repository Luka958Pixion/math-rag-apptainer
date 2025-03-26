from asyncio import run

from text_generation import AsyncClient


async def main():
    client = AsyncClient('http://0.0.0.0:8000')
    prompt = 'Tell me a joke.'
    response = await client.generate(prompt, max_new_tokens=50)
    print('Generated Text:', response.generated_text)


if __name__ == '__main__':
    run(main())
