from fastapi import FastAPI, File, UploadFile, BackgroundTasks ,HTTPException
from fastapi.responses import JSONResponse,RedirectResponse
from pdf_extractor import Extractor, BatchProcessor
from detect_Lang import DetectLanguage
import os , uuid , json
from datetime import datetime
from dotenv import load_dotenv
from cleanup import cleanup_files

app = FastAPI()
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

#------------------------------------------ Modifying Response File ------------------------------------------
def modifyResponseFile(response,job_id):
    if response["data"] != []:
        response["status"] = 1 # set status = 1, porcessed and successfull

    response["updatedAt"] = datetime.now().astimezone().isoformat() # updating updatedAt

    with open( "Outputs/"+job_id+".json", "w", encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

#------------------------------------------ Process function ------------------------------------------
def process_file(response,file_path: str, result_file_name: str, job_id: str):
    print("Process file FUNCTION")

    response["status"] = 2 # set status = 2 , processed
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}")
        response["language"] = "File Not Found, Unable to detect language" # set language 
        modifyResponseFile(response,job_id)

    detector = DetectLanguage(api_key)
    language = detector.detect_pdf_lang(file_path)

    response["language"] = language # set language attribute
   
    if(language ==  "unsupported_language"):
        print("Language Not supported")
        modifyResponseFile(response,job_id)
        
    # Simulate API Call
    processor = BatchProcessor(api_key,language)
    data = processor.process_pdf_in_batches(file_path)

    response["data"] = data

    modifyResponseFile(response,job_id)
    os.unlink(file_path)
    print(" deleted file "+ file_path)

#------------------------------------------ LOAD METADATA ------------------------------------------
@app.get("/metadata") # USED IN RESPONSE
def load_metadata():
    try:
        with open("metadata_list.json", "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#------------------------------------------ SAVING METADATA ------------------------------------------
def save_metadata(metadata):
    print("SAVING METADATA")
    try:
        with open("metadata_list.json", "r") as f:
            existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = []
    except json.JSONDecodeError:
        existing_data = []

    existing_data.append(metadata)

    with open("metadata_list.json", "w") as f:
        json.dump(existing_data, f, indent=4)

# ----------------------------------------- Ensure uploads directory exists ------------------------------------------
uploadSave_Directory = os.path.join(os.path.dirname(__file__), 'tempUploads')
os.makedirs(uploadSave_Directory, exist_ok=True)

@app.get('/')
async def read_root():
    return JSONResponse(content={'message': "Welcome to Chapter Title Extractor"}, status_code=200)


# ---------------------------------------- Upload file ------------------------------------------
@app.post('/upload')
async def upload_file( background_tasks: BackgroundTasks, file: UploadFile = File(...) ):
    # ---------------------------- Cleaning old files ----------------------------
    cleanup_files()

    job_id = str(uuid.uuid4())
    file_location = os.path.join(uploadSave_Directory, file.filename )
    with open(file_location, 'wb') as buffer:
        buffer.write(file.file.read())


    json_file_name = "Outputs/"+job_id+".json"

    metadata = {
        "job_id": job_id,
        "original_file": file_location,
        "response": json_file_name,
        "upload_timestamp": datetime.now().astimezone().isoformat()
    }
    save_metadata(metadata)
    
    response = {
    "status" : 0,
    "data" : [],
    "createdAt" : datetime.now().astimezone().isoformat(),
    "updatedAt" : datetime.now().astimezone().isoformat()
    }

    with open( json_file_name, "w", encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

    background_tasks.add_task(process_file, response , file_location, json_file_name, job_id)

    return JSONResponse(content={"Message":"File uploaded Successfully","job_id":job_id},status_code=200)


# ---------------------------------------- Get Response ------------------------------------------
@app.get("/response/{job_id}")
async def get_status(job_id: str):
    print("calling metadata function for job_id: ", job_id)
    metadata_list = load_metadata()
    metadata = next((item for item in metadata_list if item["job_id"] == job_id), None)
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")

    with open(metadata["response"], "r", encoding="utf-8") as f:
        data = json.load(f)

    return JSONResponse(content=data)

