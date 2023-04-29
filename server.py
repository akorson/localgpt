from flask import Flask, render_template, request, jsonify
from chatgpt_api import process_input_data

app = Flask(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/process_data", methods=["POST"])
def process_data():
    input_data = request.json["inputData"]
    response = process_input_data(input_data)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
