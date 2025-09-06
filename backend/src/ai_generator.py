import os
import json

from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_challenge_with_ai(difficulty: str) -> Dict[str, Any]:
    system_prompt = """You are an expert coding challenge creator. 
    Your task is to generate a coding question with multiple choice answers.
    The question should be appropriate for the specified difficulty level.

    For easy questions: Focus on basic syntax, simple operations, or common programming concepts.
    For medium questions: Cover intermediate concepts like data structures, algorithms, or language features.
    For hard questions: Include advanced topics, design patterns, optimization techniques, or complex algorithms.

    Return the challenge in the following JSON format:
    {{
      "title": "The question title",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "correct_answer_id": 0,
      "explanation": "Detailed explanation of why the correct answer is right"
    }}
    
    Only return valid JSON. Do not include markdown, code fences, or commentary.
    In "title" there should be both the question and the code of the question.
    
    Make sure the options are plausible but with only one clearly correct answer.

    should be something like this, don't add formatting words like python or ```, not in the options neither in the title
    {
            "title": "Basic Python List Operation",
            "options": [
                "my_list.append(5)",
                "my_list.add(5)",
                "my_list.push(5)",
                "my_list.insert(5)",
            ],
            "correct_answer_id": 0,
            "explanation": "In Python, append() is the correct method to add an element to the end of a list."
    }
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
        response = model.generate_content(system_prompt)

        # Gemini returns a text blob, so we need to extract and parse the JSON
        raw_text = response.text.strip()

        # Optional: clean up if Gemini wraps it in triple backticks
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:].strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3].strip()

        challenge_data = json.loads(raw_text)
        challenge_data["title"] = clean_title(challenge_data["title"])

        required_fields = ["title", "options", "correct_answer_id", "explanation"]
        for field in required_fields:
            if field not in challenge_data:
                raise ValueError(f"Missing required field: {field}")

        return challenge_data

    except Exception as e:
        print(e)
        return {
            "title": "Basic Python List Operation",
            "options": [
                "my_list.append(5)",
                "my_list.add(5)",
                "my_list.push(5)",
                "my_list.insert(5)",
            ],
            "correct_answer_id": 0,
            "explanation": "In Python, append() is the correct method to add an element to the end of a list."
        }

def clean_title(title: str) -> str:
    # Remove common formatting artifacts
    title = title.strip()
    if title.startswith("```python"):
        title = title[len("```python"):].strip()
    elif title.startswith("```"):
        title = title[3:].strip()
    if title.endswith("```"):
        title = title[:-3].strip()
    return title