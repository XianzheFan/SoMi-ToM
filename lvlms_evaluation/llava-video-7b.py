# pip install git+https://github.com/LLaVA-VL/LLaVA-NeXT.git
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN, IGNORE_INDEX
from llava.conversation import conv_templates, SeparatorStyle
from PIL import Image
import requests
import copy
import torch
import sys
import warnings
from decord import VideoReader, cpu
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

max_frames_num = 64
video_path = "Videos/20250116_1548.mp4"
video, frame_time, video_time = load_video(video_path, max_frames_num, 1, force_sample=True)
video = image_processor.preprocess(video, return_tensors="pt")["pixel_values"].cuda().bfloat16()
video = [video]
conv_template = "qwen_1_5"
time_instruciton = f"The video lasts for {video_time:.2f} seconds, and {len(video[0])} frames are uniformly sampled from it. These frames are located at {frame_time}.Please answer the following questions related to this video."

questions = [
    # "Please choose one of the three options and OUTPUT ONLY THE LETTER (A or B or C). Are the people in the video in a A. cooperative, B. competitive, or C. independent relationship?",
    # "What is the final task goal of the people in the video? A. Craft planks B. Collect stones C. Craft a wooden pickaxe. Please choose one of the three options and output only the letter.",
    # "Who crafted the first wooden pickaxe? A. Jack B. Jane C. John. Please choose one of the three options and output only the letter.",
    # "Please choose one of the three options and OUTPUT ONLY THE LETTER (A or B or C). What did Jack do in the video? A. Craft a stone pickaxe B. Craft a crafting table C. Craft a wooden pickaxe.",
    # "Please choose one of the three options and OUTPUT ONLY THE LETTER (A or B or C). What did Jane do in the video? A. Mine stones B. Craft a crafting table C. Craft wooden pickaxes.",
    # "Please choose one of the three options and OUTPUT ONLY THE LETTER (A or B or C). What did John do in the video? A. Collect birch logs B. Craft a crafting table C. Craft wooden pickaxes.",
    "Are the people in the video in a A. cooperative, B. competitive, or C. independent relationship?",
    "What do you believe is the final task goal of the people in the video? A. Craft planks B. Collect stones C. Craft a wooden pickaxe.",
    "Who do you believe crafted the first wooden pickaxe? A. Jack B. Jane C. John.",
    "What do you believe Jack did in the video? A. Craft a stone pickaxe B. Craft a crafting table C. Craft a wooden pickaxe.",
    "What do you believe Jane did in the video? A. Mine stones B. Craft a crafting table C. Craft wooden pickaxes.",
    "What do you believe John did in the video? A. Collect birch logs B. Craft a crafting table C. Craft wooden pickaxes."
]

def extract_option(result):
    result = result.upper()
    if 'A' in result:
        return 'A'
    elif 'B' in result:
        return 'B'
    elif 'C' in result:
        return 'C'
    else:
        return None

options = []
for question in questions:
    full_question = DEFAULT_IMAGE_TOKEN + time_instruciton + question + " Please THINK STEP BY STEP and choose one of the three options."
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
    # option = extract_option(text_output)
    print("\n---------------------\n")
    print(text_output)
    # options.append(option)

# concatenated_options = ''.join([opt for opt in options if opt])
# print(concatenated_options)