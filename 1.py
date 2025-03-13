import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GROQ_API_KEY")

# Check if the key is loaded
if not api_key:
    raise ValueError("GROQ_API_KEY is missing. Check your .env file.")

# Initialize Groq client
client = Groq(api_key=api_key)

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the importance of fast language models."}
    ],
    model="llama-3.3-70b-versatile",  # Ensure this model exists
)

print(chat_completion.choices[0].message.content)
