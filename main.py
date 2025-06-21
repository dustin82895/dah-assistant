
from flask import Flask, render_template, request, redirect, session, jsonify
import os
import importlib.util

app = Flask(__name__)
app.secret_key = "supersecurekey"
PASSWORD = "dahonly"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session['logged_in'] = True
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid password.")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    tool_name = request.json.get("tool")
    try:
        path = f"plugins/{tool_name}.py"
        if not os.path.exists(path):
            return jsonify({"error": "Tool not found"}), 404
        spec = importlib.util.spec_from_file_location("tool", path)
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        output = tool.run()
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
