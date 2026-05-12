import os
from openai import OpenAI

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama"
)

def get_llm_mimicry(messages: list[str], context: str = "") -> str:
    formatted = '\n'.join(f"- {msg}" for msg in messages)

    response = client.chat.completions.create(
        model="gemma2:27b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are pretending to be a Discord user. "
                    "You will be given their real messages. "
                    "Study how they actually type — their spelling, "
                    "capitalization, punctuation, abbreviations, "
                    "sentence length, topics, humor, and energy level. "
                    "Then produce ONE message that could pass as theirs. "
                    "Do not be generic. Do not be robotic. Do not be proper. "
                    "Match their vibe exactly, even if it's messy or weird. "
                    "Output ONLY the raw message text, nothing else. "
                    "No commentary. No quotes. No explanation. "
                    "NEVER include URLs, links, or GIF links."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Here are their real messages:\n{formatted}\n\n"
                    f"Write one message as this person."
                    + (f" The topic is: \"{context}\"" if context else "")
                )
            }
        ],
        temperature=0.9,
    )

    return response.choices[0].message.content