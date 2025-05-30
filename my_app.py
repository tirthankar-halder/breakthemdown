from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from mailersend import emails
import os
my_app = Flask(__name__)
CORS(my_app)

# Configure PostgreSQL
#my_app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://btd_chat_hist_user:pi3MPN4DHB5MZ8u5xPFQE5s6ITi8DN9v@dpg-cvetm0hopnds73eipr40-a/instruction_db"
#my_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#db = SQLAlchemy(my_app)

#Configure Email
MAILERSEND_API_TOKEN = os.environ.get("MAILERSEND_API_TOKEN")
FROM_EMAIL = os.environ.get("FROM_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")

# Configure API Key for Open AI
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

#class InstructionHistory(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    instruction = db.Column(db.Text, nullable=False)
#    steps = db.Column(db.ARRAY(db.Text), nullable=False)
#    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Main API to LLM
@my_app.route("/breakdown", methods=["POST"])
def breakdown_instruction():
    data = request.json
    instruction = data.get("instruction")

    if not instruction:
        return jsonify({"error": "Instruction is required"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Break down the following instruction into single line concise steps without any salutation:\n{instruction}"}]
        )

        steps = response.choices[0].message.content.strip().split("\n")

        # Save to database
        #new_entry = InstructionHistory(instruction=instruction, steps=steps)
        #db.session.add(new_entry)
        #db.session.commit()

        return jsonify({"steps": steps})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Send email to Contact API
@my_app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not all([name, email, message]):
        return jsonify({"error": "All fields required"}), 400

    try:
        mailer = emails.NewEmail(MAILERSEND_API_TOKEN)

        mailer.set_from(FROM_EMAIL, "BreakThemDown Contact")
        mailer.set_subject("BTD: New Contact Message from App")
        mailer.set_html(f"""
            <h2>New Contact Submission</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Message:</strong><br>{message}</p>
        """)
        mailer.set_to([{"email": TO_EMAIL, "name": "Your Team"}])

        result = mailer.send()
        print("MailerSend response:", result)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("MailerSend error:", e)
        return jsonify({"error": str(e)}), 500

#@my_app.route("/history", methods=["GET"])
#def get_history():
#    history = InstructionHistory.query.order_by(InstructionHistory.created_at.desc()).limit(10).all()
#    return jsonify([
#        {"instruction": h.instruction, "steps": h.steps, "created_at": h.created_at} for h in history
#    ])

if __name__ == "__main__":
    db.create_all()
    port = int(os.environ.get("PORT", 5000))
    my_app.run(host="0.0.0.0", port=port)
