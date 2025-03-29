from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
my_app = Flask(__name__)
CORS(my_app)

# Configure PostgreSQL
my_app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://btd_chat_hist_user:pi3MPN4DHB5MZ8u5xPFQE5s6ITi8DN9v@dpg-cvetm0hopnds73eipr40-a/instruction_db"
my_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(my_app)

# Configure API Key for Open AI
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

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
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Break down the following instruction into single line steps:\n{instruction}"}]
        )

        steps = response.choices[0].message.content.strip().split("\n")

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
    port = int(os.environ.get("PORT", 5000))
    my_app.run(host="0.0.0.0", port=port)
