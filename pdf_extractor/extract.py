import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from .prompt import Prompt


class Extractor:
    
   def __init__(self, api_key,language):

      load_dotenv()
        
      if not api_key:
         raise ValueError("API key is required.")
        
      self.api_key = api_key
      self.language = language
      genai.configure(api_key=api_key)
      if language == "English":
         self.model = genai.GenerativeModel("gemini-2.0-flash")
      else:
         self.model = genai.GenerativeModel("gemini-2.5-pro")
      handler = Prompt()
      self.prompt = handler.langPrompt(language)

    
   def extract_headings(self, batch_text):
      self.prompt += f"""
      {batch_text}"""

      print(f"Sending batch to Gemini API... ")
      try:
         if self.language == "Malayalam": #######################################################################################
            response = self.model.generate_content(prompt)
            raw_json_string = response.text.strip()

            # Strip markdown fences if they exist
            if raw_json_string.startswith("```json"):
               raw_json_string = raw_json_string[len("```json"):].strip()
            if raw_json_string.endswith("```"):
               raw_json_string = raw_json_string[:-len("```")].strip()

               # Parse JSON to validate
            

            try:
               parsed_json = json.loads(raw_json_string)
               return parsed_json
            except json.JSONDecodeError as e:
               print(f"JSON parsing error: {e}")
               return []
         else:
            return []

      except Exception as e:
         print(f"Error during Heading extraction: {e}")
         return []
