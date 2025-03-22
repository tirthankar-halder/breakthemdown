from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


my_app = Flask(__name__)
CORS(app)

# Configure PostgreSQL
my_app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://username:password@localhost/instruction_db"
my_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

openai.api_key = "your_openai_api_key"

class InstructionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instruction = db.Column(db.Text, nullable=False)
    steps = db.Column(db.ARRAY(db.Text), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@my_app.route("/breakdown", methods=["POST"])
def breakdown_instruction():
    data = request.json
    instruction = data.get("instruction")

    if not instruction:
        return jsonify({"error": "Instruction is required"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Break down the following instruction into steps:\n{instruction}"}]
        )

        steps = response["choices"][0]["message"]["content"].strip().split("\n")

        # Save to database
        new_entry = InstructionHistory(instruction=instruction, steps=steps)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"steps": steps})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@my_app.route("/history", methods=["GET"])
def get_history():
    history = InstructionHistory.query.order_by(InstructionHistory.created_at.desc()).limit(10).all()
    return jsonify([
        {"instruction": h.instruction, "steps": h.steps, "created_at": h.created_at} for h in history
    ])

if __name__ == "__main__":
    db.create_all()
    my_app.run(debug=True)
