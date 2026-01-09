import os
from google import genai

# 1. Setup the Client
# If your key is in an environment variable, you can just call genai.Client()
api_key = os.environ.get("GEMINI_API_KEY") or "AIzaSyDKRMUJ0tSKGsf3Cl2YBFQVIzHSSlY1XtI"
client = genai.Client(api_key=api_key)

# 2. Define your model and prompt
model_id = "gemini-2.5-flash"
user_prompt = "What is SysML v2, and what kinds of system concerns (structure, behavior, requirements, analysis, verification) is it intended to model?"

def generate_flash_response(prompt):
    try:
        # 3. Generate the content
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        # 4. Access and return the text result
        return response.text
        
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    print(f"--- Sending prompt to {model_id} ---")
    result = generate_flash_response(user_prompt)
    print(f"\nResponse:\n{result}")