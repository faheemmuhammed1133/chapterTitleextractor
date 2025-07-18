class Prompt():
   def langPrompt(self, language):
      if language == "Malayalam":
         prompt = """
            You are a chapter heading extractor for Malayalam NCERT textbook.

            Extract all chapter headings from the text below and return them as a JSON array ONLY.

            Each item in the array should include the following keys:
            - "title": The complete chapter title in Malayalam, cleaned and properly formatted.
            - "page_number": The page number where this heading appears, the actual page number of PDF (represented as --- Page x ---) .

            Important extraction rules:
            - Extract ONLY actual chapter headings (Don't take headings from the table of contents page , only take the headings from where the chapter actually begins), not paragraph text, questions, or descriptions.
            - Clean up any formatting issues or OCR errors in the Malayalam text.
            - Ensure proper Malayalam Unicode formatting.Convert legacy text to it's approptiate Malayalam unicode text.
            - Ignore the Unit headings , sometimes it can contain text with it , still ignore!! May it will be mentioned in the text below it ,this unit has this stuff "", likeways.

            Response format:
            - Return ONLY a valid JSON array string, no additional text, comments, or markdown formatting.
            - If no headings are found, return an empty array: []
            - Ensure the JSON is properly formatted and can be parsed directly.

            Input chunk:
         """
      elif language == "Hindi":
         prompt = """
         
         """
      elif language == "English":
            prompt = """
         
         """
      elif language == "Arabic":
         prompt = """
         
         """
      elif language == "Urdu":
         prompt = """
         
         """
      else:
         return ""
      
      return prompt