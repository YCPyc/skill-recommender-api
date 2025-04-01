from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["POST"])
def get_writing_skill():
    if request.method == "POST":
        data = request.get_json()
        writingSkills = data["writingSkills"]
        writingSample = data["writingSample"]
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": "Recommend a writing skill that the writer needs to work on based on the writing sample."},
                {"role": "user", "content": f"Please analyze the writing skills and the writing sample. Based on the writing sample, please provide a recommneded skill from the list of skills that the writer needs to work on. Writing Skills: {writingSkills}\nWriting Sample: {writingSample}"}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "calendar_event",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "skill": {
                                "type": "string"
                            },
                        },
                        "required": ["skill"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )
        event = json.loads(response.output_text)
        response = {
            "status": "success",
            "message": event["skill"]
        }
        return jsonify(response)
    else:
        response = {
            "status": "error",
            "message": "Please use POST method"
        }
        return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
