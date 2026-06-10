import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "google/gemini-2.0-flash-exp:free"

history = [
    {"role": "system", "content": "You are a helpful Python tutor."}
]

print("CLI Chatbot 已启动，输入 quit 退出\n")

while True:
    user_input = input("You: ")

    if user_input.strip().lower() == "quit":
        print("再见！")
        break

    history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
    )

    reply = response.choices[0].message.content
    print(f"AI: {reply}\n")

    history.append({"role": "assistant", "content": reply})
