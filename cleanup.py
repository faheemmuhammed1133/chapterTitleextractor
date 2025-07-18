import os
import json
from datetime import datetime, timedelta , timezone

def cleanup_files(max_age_hours=24):
    try:
        # Read metadata
        with open("metadata_list.json", "r") as f:
            metadata_list = json.load(f)
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        files_to_remove = []
        
        for metadata in metadata_list:
            try:
                # Check JSON file age
                json_path = metadata["response"]
                if not os.path.exists(json_path):
                    continue
                    
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                
                updated_at = datetime.fromisoformat(json_data["updatedAt"])
                
                # If file is old enough, delete it
                if updated_at < cutoff_time:
                    # Delete JSON file
                    os.unlink(json_path)
                    
                    files_to_remove.append(metadata["job_id"])
                    print(f"Deleted files for job: {metadata['job_id']}")
                    
            except Exception as e:
                print(f"Error processing {metadata.get('job_id', 'unknown')}: {e}")
        
        # Update metadata file
        if files_to_remove:
            updated_metadata = [m for m in metadata_list if m["job_id"] not in files_to_remove]
            with open("metadata_list.json", "w") as f:
                json.dump(updated_metadata, f, indent=4)
            print(f"Removed {len(files_to_remove)} entries from metadata")
                
    except Exception as e:
        print(f"Cleanup error: {e}")