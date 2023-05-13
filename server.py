
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from chatgpt_api import process_input_data

app = Flask(__name__)

# Load environment variables from .env file

load_dotenv()


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process_data", methods=["POST"])
def process_data():
    try:
        input_data = request.json["inputData"]
        response = process_input_data(input_data)
        return jsonify(response), 200
    except KeyError:
        return jsonify({"error": "Input data not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
