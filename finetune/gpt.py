import os
import json
import openai
from openai import OpenAI

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

def upload_training_data(file_path):
    file = client.files.create(file=open(file_path), purpose='fine-tune')
    return file.id

def fine_tune_model(training_file_id, model="gpt-4o-mini-2024-07-18"):
    fine_tune_job = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        model=model
    )
    return fine_tune_job

if __name__ == "__main__":
    training_data = prepare_training_data(photo_dir)
    save_to_jsonl(training_data, "training_data.jsonl")
    file_id = upload_training_data("training_data.jsonl")
    print(f"Uploaded training data file with ID: {file_id}")
    fine_tune_job = fine_tune_model(file_id)
    print(f"Fine-tuning job started: {fine_tune_job['id']}")
