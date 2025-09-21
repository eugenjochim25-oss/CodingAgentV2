from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    response = f"Agent: Ich habe deine Nachricht erhalten -> {user_message}"
    return jsonify({"response": response})

@app.route("/execute", methods=["POST"])
def execute_code():
    code = request.json.get("code", "")
    file_path = "temp_script.py"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        result = subprocess.run(["python", file_path], capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
    except Exception as e:
        output = str(e)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    return jsonify({"output": output})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
