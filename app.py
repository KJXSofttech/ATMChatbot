from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chat_flow import get_chat_response
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def chat_response():
    return get_chat_response(request.json)

@app.route("/start_conversation", methods=["POST"])
def start_conversation():
    return get_chat_response({"current_tag": "start_conversation"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 4000))
    app.run(debug=True, host='0.0.0.0', port=port)
