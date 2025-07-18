import uuid
import pdfplumber
import os
from .extract import Extractor


# ------------------------------ PDF Reading Logic ------------------------------

class BatchProcessor:  
    def __init__(self, api_key,language, pages_per_batch=15):
     
        self.pages_per_batch = pages_per_batch
        self.extractor = Extractor(api_key,language)

    #  ```````````````````create batches``````````````````
    def create_batches(self, pdf_path):
        print("Creating page-based batches...")
        
        batches = []
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages in PDF: {total_pages}")

            # Create batches of pages without overlap
            for i in range(0, total_pages, self.pages_per_batch):
                batch_start_page = i
                batch_end_page = min(i + self.pages_per_batch, total_pages)
                
                # Extract text from pages in this batch
                batch_text = ""
                for page_num in range(batch_start_page, batch_end_page):
                    page_text = pdf.pages[page_num].extract_text()
                    if page_text:
                        batch_text += f"\n--- Page {page_num + 1} ---\n"
                        batch_text += page_text + "\n"
                
                # Creation of batch object
                batch = {
                    'batch_number': len(batches) + 1,
                    'start_page': batch_start_page + 1,  # 1-indexed for display
                    'end_page': batch_end_page,          # 1-indexed for display
                    'text': batch_text,
                    'char_count': len(batch_text)
                }

                batches.append(batch)
                print(f"Created batch {batch['batch_number']}: Pages {batch['start_page']}-{batch['end_page']} "
                      f"({len(batch_text)} chars)")
                
        return batches
    
    def process_pdf_in_batches(self, pdf_path):       
        print(f"\n\t Processing PDF {pdf_path} \t\t")

        # Create page-based batches
        batches = self.create_batches(pdf_path)
        print(f"Created {len(batches)} batches")
        
        if not batches:
            print("No batches created")
            return []

        all_extracted_headings = []
        
        for batch in batches:
            print(f"\nProcessing batch {batch['batch_number']} (Pages {batch['start_page']}-{batch['end_page']})...")
            
            if len(batch['text']) == 0:
                print("No text found in this batch, skipping...")
                continue
            
            batch_results = self.extractor.extract_headings(batch["text"])
            # batch_results =  [
            #     {
            #         "title": "ariv",
            #         "page_number":7
            #     },
            #     {
            #         "title": "niyal",
            #         "page_number":13
            #     },
            #     {
            #         "title": "nilav",
            #         "page_number":19
            #     }
            # ]
            # if( batch_results):
            print(f"Extracted {len(batch_results)} headings from batch {batch['batch_number']}")
            all_extracted_headings.extend(batch_results)
            print("")
        
        # ------------- Add chapter numbers / unique id   -------------
        for i, heading in enumerate(all_extracted_headings):

            heading["chapter_number"] = i + 1
            heading["chapter_id"] = str(uuid.uuid4())

            topics = [{
                "topic_id" : heading["chapter_id"],
                "topic" : heading["title"],
                "questions" : []
            }]

            heading["topics"] = topics


        print(f"\nTotal headings extracted: {len(all_extracted_headings)}")
        # print("\n\t"+all_extracted_headings)
        return all_extracted_headings
