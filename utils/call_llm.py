from openai import OpenAI
import os

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(prompt):    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    r = client.chat.completions.create(
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
    
if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))
