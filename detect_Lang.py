import google.generativeai as genai
import pdfplumber
import base64
import io

class DetectLanguage:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
    def detect_pdf_lang(self, file_path):
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract text from first page using pdfplumber
                pages_to_check = 1
                for page_num in range(pages_to_check):
                    page = pdf.pages[page_num]
                    image = page.to_image()
                    pil_image = image.original
                
                # Convert PIL image to base64
                img_buffer = io.BytesIO()
                pil_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                image_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
                
                # Configure Gemini
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                # Create the image part for Gemini
                image_part = {
                    "mime_type": "image/png",
                    "data": image_base64
                }
                
                # Create prompt for language detection
                prompt = """
                You are an expert linguist with deep knowledge of language identification. Analyze the text in this image and determine its written language using your contextual understanding of script patterns, vocabulary, grammar, and linguistic structures.

                The text may contain one of these languages:
                - English
                - Hindi  
                - Malayalam
                - Arabic
                - Urdu

                Based on your linguistic expertise analysis, identify the primary language. Respond with only ONE word from the exact options above.
                """
                prompt = """
                You are an expert linguist with deep knowledge of language identification. Analyze the text in this image and determine its written language using your contextual understanding of script patterns, vocabulary, grammar, and linguistic structures.

                The text may contain one of these languages:
                - English
                - Hindi  
                - Malayalam
                - Arabic
                - Urdu

                Based on your linguistic expertise analysis, identify the primary language. Respond with only ONE word from the exact options above.
                """
                
                # Get response from Gemini with image
                response = model.generate_content([prompt, image_part])
                detected_language = response.text.strip()
                
                
                # Validate response
                if detected_language in ['English', 'Hindi', 'Malayalam', 'Arabic', 'Urdu']:
                    return detected_language
                else:
                    return "unsupported_language"
                
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return "error"

# Example usage:
# detector = DetectLanguage("your_api_key_here")
# result = detector.detect_pdf_lang("path_to_your_pdf.pdf")
# print(f"Detected language: {result}")