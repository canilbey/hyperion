import os
import openai

class LlmService:
    def __init__(self, api_key: str = None, model: str = 'gpt-3.5-turbo'):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        openai.api_key = self.api_key

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message["content"].strip() 