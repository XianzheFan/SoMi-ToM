# pip install git+https://github.com/LLaVA-VL/LLaVA-NeXT.git
from llava.model.builder import load_pretrained_model
from llava.mm_utils import tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
from llava.conversation import conv_templates
import copy
import warnings
from decord import VideoReader, cpu
import os
import pandas as pd
import numpy as np
warnings.filterwarnings("ignore")

def load_video(video_path, max_frames_num, fps=1, force_sample=False):
    if max_frames_num == 0:
        return np.zeros((1, 336, 336, 3))
    vr = VideoReader(video_path, ctx=cpu(0), num_threads=1)
    total_frame_num = len(vr)
    video_time = total_frame_num / vr.get_avg_fps()
    fps = round(vr.get_avg_fps() / fps)
    frame_idx = [i for i in range(0, len(vr), fps)]
    frame_time = [i / vr.get_avg_fps() for i in frame_idx]
    if len(frame_idx) > max_frames_num or force_sample:
        sample_fps = max_frames_num
        uniform_sampled_frames = np.linspace(0, total_frame_num - 1, sample_fps, dtype=int)
        frame_idx = uniform_sampled_frames.tolist()
        frame_time = [i / vr.get_avg_fps() for i in frame_idx]
    frame_time = ",".join([f"{i:.2f}s" for i in frame_time])
    spare_frames = vr.get_batch(frame_idx).asnumpy()
    return spare_frames, frame_time, video_time

pretrained = "lmms-lab/LLaVA-Video-7B-Qwen2"
model_name = "llava_qwen"
device = "cuda"
device_map = "auto"
tokenizer, model, image_processor, max_length = load_pretrained_model(pretrained, None, model_name, torch_dtype="bfloat16", device_map=device_map)
model.eval()

def send_video_to_llava(video_path, question, max_frames_num=64):
    video, frame_time, video_time = load_video(video_path, max_frames_num, 1, force_sample=True)
    video = image_processor.preprocess(video, return_tensors="pt")["pixel_values"].cuda().bfloat16()
    video = [video]
    conv_template = "qwen_1_5"
    time_instruciton = f"The video lasts for {video_time:.2f} seconds, and {len(video[0])} frames are uniformly sampled from it. These frames are located at {frame_time}.Please answer the following questions related to this video."
    
    full_question = DEFAULT_IMAGE_TOKEN + time_instruciton + question
    conv = copy.deepcopy(conv_templates[conv_template])
    conv.append_message(conv.roles[0], full_question)
    conv.append_message(conv.roles[1], None)
    prompt_question = conv.get_prompt()
    input_ids = tokenizer_image_token(prompt_question, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt").unsqueeze(0).to(device)
    
    cont = model.generate(
        input_ids,
        images=video,
        modalities=["video"],
        do_sample=False,
        temperature=0,
        max_new_tokens=256,
    )
    
    text_output = tokenizer.batch_decode(cont, skip_special_tokens=True)[0].strip()
    return text_output

# def process_excel_file(excel_path, video_base_path=None, num_frames=25, output_file="llava_videoqa.txt"):
def process_excel_file(excel_path, video_base_path=None, num_frames=25, output_file="llava_cot_videoqa.txt"):
    df = pd.read_excel(excel_path, header=None)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("LLaVA Video QA Results\n")
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
                        # full_question = f"{question} Please choose one of the three options and output only the letter."
                        full_question = f"{question} Please think STEP BY STEP and choose one of the three options."
                        
                        result = send_video_to_llava(video_path, full_question)
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