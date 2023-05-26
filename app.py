from helperFunctions import *
from flask import Flask, render_template, request, redirect, Response, url_for
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
conversation = openai_set_memory_respond()


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


@app.route("/process-message", methods=["POST"])
def process_prompt_route():
    return None


@app.route("/process-requirement", methods=["POST"])
def process_requirement_route():
    return None


@app.route("/process-openai-review", methods=["POST"])
def process_openai_review_route():
    return None


@app.route("/process-google-review", methods=["POST"])
def process_google_review_route():
    return None


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    return None


@app.route("/text-to-speech", methods=["POST"])
def text_to_speech_route():
    return None


if __name__ == "__main__":
    app.run(debug=False, use_reloader=True, port=9090, host="0.0.0.0")
