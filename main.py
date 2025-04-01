from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def validate_input(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate the input data."""
    if not data:
        return False, "No data provided"
    
    if "writingSample" not in data:
        return False, "Missing 'writingSample' in request"
    
    if not isinstance(data["writingSample"], str):
        return False, "'writingSample' must be a string"
    
    return True, ""

@app.route("/", methods=["POST"])
def get_writing_skill():
    try:
        # Check if request is JSON
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 400

        # Get and validate input data
        data = request.get_json()
        is_valid, error_message = validate_input(data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "message": error_message
            }), 400

        writingSample = data["writingSample"]

        # Define available skills
        available_skills = [
            "Adding relevant details",
            "Organizing ideas clearly",
            "Using transitions",
            "Writing strong introductions",
            "Writing strong conclusions",
            "Varying sentence structure",
            "Using precise language",
            "Staying on topic",
            "Supporting ideas with evidence"
        ]

        try:
            response = client.responses.create(
                model="gpt-4o",
                input=[
                    {"role": "system", "content": "Recommend a writing skill that the writer needs to work on based on the writing sample."},
                    {"role": "user", "content": f"Please analyze the writing skills and the writing sample. Based on the writing sample, please provide a recommneded skill from the list of skills that the writer needs to work on. Writing Skills: {available_skills}\nWriting Sample: {writingSample}"}
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
            
            # Validate that the recommended skill is in our list
            if event["skill"] not in available_skills:
                return jsonify({
                    "status": "error",
                    "message": "Invalid skill recommendation received"
                }), 500

            return jsonify({
                "status": "success",
                "message": event["skill"]
            })

        except json.JSONDecodeError:
            return jsonify({
                "status": "error",
                "message": "Invalid response format from AI service"
            }), 500
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error from AI service: {str(e)}"
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
