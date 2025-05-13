import torch
from transformers import AutoModelForCausalLM, AutoProcessor

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

video_path = "Videos/20250116_1349.mp4"
result_1 = send_video_to_videollama(video_path, "Are the people in the video in a A. cooperative, B. competitive, or C. independent relationship? Please choose one of the three options and output only the letter.")
result_2 = send_video_to_videollama(video_path, "What is the final task goal of the people in the video? A. Craft a crafting table B. Craft a wooden pickaxe C. Collect stones. Please choose one of the three options and output only the letter.")
result_3 = send_video_to_videollama(video_path, "Who crafted the first wooden pickaxe? A. Jack B. Jane C. John. Please choose one of the three options and output only the letter.")
result_4 = send_video_to_videollama(video_path, "What did Jack do in the video? A. Craft a stone pickaxe B. Craft a chest C. Craft a wooden pickaxe. Please choose one of the three options and output only the letter.")
result_5 = send_video_to_videollama(video_path, "What did Jane do in the video? A. Craft a stone pickaxe B. Craft a crafting table C. Craft a wooden pickaxe. Please choose one of the three options and output only the letter.")
result_6 = send_video_to_videollama(video_path, "What did John do in the video? A. Craft oak planks B. Craft a crafting table C. Craft a wooden pickaxe. Please choose one of the three options and output only the letter.")

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
results = [result_1, result_2, result_3, result_4, result_5, result_6]
for i, result in enumerate(results):
    option = extract_option(result)
    options.append(option)
concatenated_options = ''.join([opt for opt in options if opt])
print(concatenated_options)