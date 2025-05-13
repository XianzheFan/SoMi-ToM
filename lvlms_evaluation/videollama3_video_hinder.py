import torch
from transformers import AutoModelForCausalLM, AutoProcessor
import pandas as pd
import os

device = "cuda:0"
model_path = "DAMO-NLP-SG/VideoLLaMA3-7B"
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    device_map={"": device},
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

def send_video_to_videollama(video_path, question):
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "video", "video": {"video_path": video_path, "fps": 2, "max_frames": 2000}},  # maximum sequence length for this model: 32768
                {"type": "text", "text": question},
            ]
        },
    ]

    inputs = processor(
        conversation=conversation,
        add_system_prompt=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )
    inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
    if "pixel_values" in inputs:
        inputs["pixel_values"] = inputs["pixel_values"].to(torch.bfloat16)
    output_ids = model.generate(**inputs, max_new_tokens=1024)
    response = processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()
    return response

def process_excel_file(excel_path, video_base_path=None, num_frames=25, output_file="output_videoqa/qwenvl_videoqa.txt"):
# def process_excel_file(excel_path, video_base_path=None, num_frames=25, output_file="output_videoqa/qwenvl_cot_videoqa.txt"):
    df = pd.read_excel(excel_path, header=None)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("QwenVL Video QA Results\n")
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
                # Process each question (columns 3-10)
                for i in range(2, 10):  # Column indices 2-9 (3rd to 10th columns)
                    if i < len(row) and pd.notna(row.iloc[i]):
                        question = row.iloc[i]
                        full_question = f"{question} Please choose one of the three options and output only the letter."
                        # full_question = f"{question} Please think step by step and choose one of the three options."
                        
                        result = send_video_to_videollama(video_path, full_question)
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
    process_excel_file(excel_path, video_base_path)