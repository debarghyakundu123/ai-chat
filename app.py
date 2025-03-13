import os
import time
import speech_recognition as sr
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from groq import Groq
from googlesearch import search
from newspaper import Article

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("❌ GROQ_API_KEY is missing. Please check your .env file.")

# Initialize Flask app and Groq AI client
app = Flask(__name__)
client = Groq(api_key=API_KEY)

# === AI RESPONSE FUNCTION ===
def ask_groq(question):
    """Ask the AI model for an answer."""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error querying AI: {e}")
        return "AI is currently unavailable. Please try again later."

# === NEWS FETCHING FUNCTION ===
def fetch_news_articles(query, num_results=3):
    """Search Google and extract news articles."""
    print("🔍 Searching for latest news...")
    
    try:
        links = list(search(query, num_results=num_results))
    except Exception as e:
        print(f"❌ Google search error: {e}")
        return []

    articles = []
    
    for link in links:
        try:
            article = Article(link)
            article.download()
            article.parse()
            articles.append(article.text)
            print(f"✅ Retrieved article from: {link}")
            time.sleep(2)  # Prevent rate limits
        except Exception as e:
            print(f"❌ Failed to fetch {link}: {e}")
    
    return articles

# === AI + NEWS PROCESSING FUNCTION ===
def get_final_answer(query):
    """Get AI response or fetch news if AI lacks real-time info."""
    ai_answer = ask_groq(query)

    if "do not have information" in ai_answer.lower() or "knowledge cutoff" in ai_answer.lower():
        print("⚠️ AI lacks real-time info. Fetching latest news...")
        articles = fetch_news_articles(query)
        
        if articles:
            news_summary = " ".join(articles[:2])  # Take first 2 articles
            final_answer = ask_groq(f"Summarize and answer this question based on the latest news: {query}\n\n{news_summary}")
        else:
            final_answer = "❌ No valid articles found. Please try again later."
    else:
        final_answer = ai_answer

    return final_answer

# === FLASK ROUTES ===
@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask_ai():
    """Handle user queries and return AI or news-based responses."""
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "⚠️ No input received. Please enter a question."})

    try:
        response = get_final_answer(user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"response": f"❌ Error processing request: {str(e)}"})

@app.route("/voice", methods=["POST"])
def voice_input():
    """Handle voice input, convert to text, and send to AI."""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            user_input = recognizer.recognize_google(audio)
            print(f"🎙️ Recognized: {user_input}")

            return jsonify({"message": user_input})
    
    except sr.UnknownValueError:
        return jsonify({"message": "⚠️ Could not understand the audio."})
    except sr.RequestError:
        return jsonify({"message": "❌ Speech Recognition service unavailable."})

# === FLASK APP RUNNER ===
if __name__ == "__main__":
    app.run(debug=True)
