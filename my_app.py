from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from mailersend import emails
import os
from dotenv import load_dotenv

my_app = Flask(__name__)
CORS(my_app)

load_dotenv()    # Load env variable

#Configure Email
MAILERSEND_API_TOKEN = os.getenv("MAILERSEND_API_TOKEN")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")

# Configure API Key for Open AI
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

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
       
        # Replace this with actual mail sending code
        print(f"Sending email: from {FROM_EMAIL} to {TO_EMAIL}")
        print(f"Subject: BTD: New Contact Message from App")
        print(f"Content: Name: {name}, Email: {email}, Message: {message}")
        print("API Key is set:", bool(os.getenv("OPENAI_API_KEY"), os.getenv("FROM_EMAIL")))
    
        mailer = emails.NewEmail(os.getenv("MAILERSEND_API_TOKEN"))
        
        mail_body = {}
        
        # Set sender
        mail_from = {
            "name": "BreakThemDown Contact",
            "email": os.getenv("FROM_EMAIL")
        }
        mailer.set_mail_from(mail_from, mail_body)
        
        # Set recipients
        recipients = [
            {
                "name": "Dyaz Team",
                "email": os.getenv("TO_EMAIL")
            }
        ]
        mailer.set_mail_to(recipients, mail_body)
        
        # Set subject
        mailer.set_subject("BTD: New Contact Message from App", mail_body)
        
        # Set HTML content
        mailer.set_html_content(f"""
            <h2>New Contact Submission</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Message:</strong><br>{message}</p>
        """, mail_body)
        
        # Send email
        result = mailer.send(mail_body)
        print("MailerSend response:", result)
        return jsonify({"status": "success", "result": result}), 200

    except Exception as e:
        print("MailerSend error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    db.create_all()
    port = int(os.environ.get("PORT", 5000))
    my_app.run(host="0.0.0.0", port=port)
