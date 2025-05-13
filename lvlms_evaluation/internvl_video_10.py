import cv2
import base64
from openai import OpenAI

# InternVL2_5_78B internvl2.5-latest
client = OpenAI(
    api_key="",  # token
    base_url="https://chat.intern-ai.org.cn/api/v1/",
)

def extract_frames_and_send_to_api(video_path, num_frames):
    video_capture = cv2.VideoCapture(video_path)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    
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

def send_images_to_internvl(frames_base64, prompt):
    content = [{"type": "text", "text": prompt}]
    
    for i, img_base64 in enumerate(frames_base64):
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}"
            }
        })
    
    try:
        response = client.chat.completions.create(
            model="internvl2.5-latest",
            messages=[{"role": "user", "content": content}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return str(e)

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
    
frames_base64 = extract_frames_and_send_to_api("Videos/20250116_1349.mp4", num_frames=10)

# result_1 = send_images_to_internvl(frames_base64, "Are the people in the video in a A. cooperative, B. competitive, or C. independent relationship? Please choose one of the three options and output only the letter.")
# result_2 = send_images_to_internvl(frames_base64, "What is the final goal of the people in the video? A. Craft 2 boats B. Collect logs C. Craft a crafting table. Please choose one of the three options and output only the letter.")
# result_3 = send_images_to_internvl(frames_base64, "Who crafted the first boat? A. Jack B. Jane C. John. Please choose one of the three options and output only the letter.")
# result_4 = send_images_to_internvl(frames_base64, "What did Jack do in the video? A. Collect logs B. Craft boats C. Craft a crafting table. Please choose one of the three options and output only the letter.")
# result_5 = send_images_to_internvl(frames_base64, "What did Jane do in the video? A. Hunt chicken B. Craft boats C. Craft a crafting table. Please choose one of the three options and output only the letter.")
# result_6 = send_images_to_internvl(frames_base64, "What did John do in the video? A. Hunt chicken B. Craft boats C. Collect birch logs. Please choose one of the three options and output only the letter.")

result_1 = send_images_to_internvl(frames_base64, "Are the people in the video in a A. cooperative, B. competitive, or C. independent relationship?" + " Please think step by step and choose one of the three options.")
result_2 = send_images_to_internvl(frames_base64, "What do you believe is the final task goal of the people in the video? A. Craft a crafting table B. Craft a wooden pickaxe C. Collect stones." + " Please think step by step and choose one of the three options.")
result_3 = send_images_to_internvl(frames_base64, "Who do you believe crafted the first wooden pickaxe? A. Jack B. Jane C. John." + " Please think step by step and choose one of the three options.")
result_4 = send_images_to_internvl(frames_base64, "What do you believe Jack did in the video? A. Craft a stone pickaxe B. Craft a chest C. Craft a wooden pickaxe." + " Please think step by step and choose one of the three options.")
result_5 = send_images_to_internvl(frames_base64, "What do you believe Jane did in the video? A. Craft a stone pickaxe B. Craft a crafting table C. Craft a wooden pickaxe." + " Please think step by step and choose one of the three options.")
result_6 = send_images_to_internvl(frames_base64, "What do you believe John did in the video? A. Craft oak planks B. Craft a crafting table C. Craft a wooden pickaxe." + " Please think step by step and choose one of the three options.")

options = []
results = [result_1, result_2, result_3, result_4, result_5, result_6]
for i, result in enumerate(results):
    print(result)
    print("\n-------------------\n")
#     option = extract_option(result)
#     options.append(option)
# concatenated_options = ''.join([opt for opt in options if opt])
# print(concatenated_options)