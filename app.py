from flask import Flask, request, jsonify
from flask_cors import CORS
from pinecone import Pinecone
import google.generativeai as genai
import os

# Flask setup
app = Flask(__name__)
CORS(app)

# Load API keys (replace with your real ones)
GOOGLE_API_KEY = "AIzaSyDSLopVluavm_ap7NU54gFd5m1aR6Oq0cI"
PINECONE_API_KEY = "pcsk_4PWhn2_bduxadqyALjZK2Nmd7ReATX8f2WuQAV8ZbAYFZ7DLZntP3PLAsKv2PHo24ieow"
PINECONE_INDEX_NAME = "nutrition-bot"

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

# Setup Pinecone client and index
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Load Gemini model
model = genai.GenerativeModel("gemini-pro")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_query = data.get("message", "")

    # Embed the user query
    embed_model = genai.embed_content(
        model="models/embedding-001",
        content=user_query,
        task_type="retrieval_query"
    )
    query_vector = embed_model["embedding"]

    # Search Pinecone for relevant context
    results = index.query(vector=query_vector, top_k=5, include_metadata=True)

    # Collect matching text from Pinecone results
    context_list = []
    for match in results.get("matches", []):
        if "text" in match.get("metadata", {}):
            context_list.append(match["metadata"]["text"])

    # If no relevant data found
    if not context_list:
        return jsonify({"response": "Sorry, I couldn't find information related to your query in our product database."})

    # Join all relevant context
    context = "\n\n".join(context_list)

    # Prompt Gemini using actual website data
    prompt = f"""
You are an expert assistant for Better Nutrition For All. Use only the context provided below to answer the user's question. Do not make up information. Keep it short and relevant to the company’s product offerings.

Context:
{context}

Question: {user_query}
Answer:
    """

    # Get answer from Gemini
    response = model.generate_content(prompt)
    return jsonify({"response": response.text.strip()})

# Run the server
if __name__ == "__main__":
    app.run(debug=True)
