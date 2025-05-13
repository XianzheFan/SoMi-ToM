import openai
import os
import base64
import pandas as pd
from openai import OpenAI
import cv2

openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()

def extract_frames_and_send_to_api(video_path, num_frames):
    video_capture = cv2.VideoCapture(video_path)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate the step size to get exactly num_frames images
    step = max(1, total_frames // num_frames)
    frames_base64 = []
    frame_indices = [i * step for i in range(num_frames)]
    
    for frame_idx in frame_indices:
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = video_capture.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        frames_base64.append(base64_image)
    
    video_capture.release()
    print(f"Total frames in video: {total_frames}")
    print(f"Total frames extracted: {len(frames_base64)}")
    return frames_base64

def send_images_to_openai(frames_base64, prompt):
    content = [{"type": "text", "text": prompt}]
    for i, img_base64 in enumerate(frames_base64):
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
        })
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[{"role": "user", "content": content}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return str(e)

# def process_excel_file(excel_path, video_base_path=None, num_frames=25, output_file="lvlms_evaluation/output_videoqa/gpt_videoqa.txt"):
def process_excel_file(excel_path, video_base_path=None, num_frames=25, output_file="lvlms_evaluation/output_videoqa/gpt_cot_videoqa.txt"):
    df = pd.read_excel(excel_path, header=None)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("GPT-4o Video QA Results\n")
        f.write("======================\n\n")
        
        for index, row in df.iterrows():
            name = row.iloc[0]  # First column contains the name
            video_file = row.iloc[1]  # Second column contains the video filename
            
            if video_base_path:
                video_path = os.path.join(video_base_path, video_file)
            else:
                video_path = video_file
            
            header = f"\n--- Processing video for {name} ({video_file}) ---\n"
            f.write(header)
            print(header)
            
            try:
                frames_base64 = extract_frames_and_send_to_api(video_path, num_frames)
                frame_info = f"Total frames in video: {len(frames_base64)}\n\n"
                f.write(frame_info)
                
                # Process each question (columns 3-10)
                for i in range(2, 10):  # Column indices 2-9 (3rd to 10th columns)
                    if i < len(row) and pd.notna(row.iloc[i]):
                        question = row.iloc[i]
                        # full_question = f"{question} Please choose one of the three options and output only the letter."
                        full_question = f"{question} Please think step by step and choose one of the three options."
                        
                        result = send_images_to_openai(frames_base64, full_question)
                        f.write(f"{result}\n")
                        print(result)
                        
                        f.write("\n------------------\n")
                        print("\n------------------\n")
            except Exception as e:
                error_msg = f"Error processing video {video_file}: {e}\n"
                f.write(error_msg)
                print(error_msg)

if __name__ == "__main__":
    excel_path = "hinder-videoqa.xlsx"
    video_base_path = "Videos/"
    process_excel_file(excel_path, video_base_path, num_frames=25)