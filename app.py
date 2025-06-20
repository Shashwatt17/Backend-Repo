import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)

model = genai.GenerativeModel("models/gemini-1.5-flash")

# ✅ Root route to avoid 404 errors on backend homepage
@app.route("/")
def index():
    return "✅ AI Nutritionist Chatbot Backend is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    try:
        response = model.generate_content(user_message)
        return jsonify({"reply": response.text})
    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "⚠️ Something went wrong on the server."}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
