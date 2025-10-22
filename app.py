from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# --- Flask setup ---
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# --- Database setup ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Task model ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)

    def to_dict(self):
        return {"id": self.id, "text": self.text}

# --- Create DB if not exists ---
with app.app_context():
    db.create_all()

# --- Serve frontend ---
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# --- API routes ---
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.order_by(Task.id).all()
    return jsonify([t.to_dict() for t in tasks]), 200

@app.route("/add", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or "text" not in data or not data["text"].strip():
        return jsonify({"error": "Missing or empty 'text' field"}), 400
    task = Task(text=data["text"].strip())
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task added", "task": task.to_dict()}), 201

@app.route("/update/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400
    t = Task.query.get(task_id)
    if not t:
        return jsonify({"error": "Task not found"}), 404
    t.text = data["text"].strip()
    db.session.commit()
    return jsonify({"message": "Task updated", "task": t.to_dict()}), 200

@app.route("/delete/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    t = Task.query.get(task_id)
    if not t:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200

# --- Optional: open browser automatically ---
if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
