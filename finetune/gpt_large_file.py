import os
import json
import openai
from openai import OpenAI
import math

openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()
photo_dir = './photo/'

def image_to_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return img_file.read()

def prepare_training_data(photo_dir):
    training_data = []
    
    for filename in os.listdir(photo_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(photo_dir, filename)
            image_data = image_to_base64(image_path)
            
            caption = f"This is an image of {filename.split('.')[0]}"
            
            training_data.append({
                "image": image_data,
                "caption": caption
            })
    
    return training_data

def save_to_jsonl(training_data, output_file="training_data.jsonl"):
    with open(output_file, 'w') as f:
        for data in training_data:
            f.write(json.dumps(data) + '\n')

def create_upload(file_path):
    file_size = os.path.getsize(file_path)
    mime_type = 'application/jsonl'

    upload = client.uploads.create(
        filename=os.path.basename(file_path),
        purpose='fine-tune',
        bytes=file_size,
        mime_type=mime_type
    )
    return upload

def upload_part(upload_id, file_path, part_size=64 * 1024 * 1024):
    file_size = os.path.getsize(file_path)
    num_parts = math.ceil(file_size / part_size)

    with open(file_path, 'rb') as file:
        part_ids = []
        for part_num in range(num_parts):
            part_data = file.read(part_size)
            part = client.uploads.parts(upload_id, data=part_data)
            part_ids.append(part.id)
        return part_ids

def complete_upload(upload_id, part_ids):
    upload = client.uploads.complete(upload_id, part_ids=part_ids)
    return upload.file.id

def fine_tune_model(training_file_id, model="gpt-4o-mini-2024-07-18"):
    fine_tune_job = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        model=model
    )
    return fine_tune_job

if __name__ == "__main__":
    training_data = prepare_training_data(photo_dir)
    save_to_jsonl(training_data, "training_data.jsonl")

    upload = create_upload("training_data.jsonl")
    print(f"Upload created with ID: {upload.id}")

    part_ids = upload_part(upload.id, "training_data.jsonl")
    print(f"Uploaded {len(part_ids)} parts.")

    training_file_id = complete_upload(upload.id, part_ids)
    print(f"Upload completed. File ID: {training_file_id}")

    fine_tune_job = fine_tune_model(training_file_id)
    print(f"Fine-tuning job started: {fine_tune_job['id']}")
