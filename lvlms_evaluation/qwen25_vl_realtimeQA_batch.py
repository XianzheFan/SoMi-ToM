from openai import OpenAI
import pandas as pd
import time
import requests
import base64
from io import BytesIO
import random

client = OpenAI(
    api_key="",  # Replace with your actual API key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

game_rule = """NOTE: !collectBlocks(material, number) only initiates the collection process, it does not guarantee that the specified material has been collected. Once the number of materials have been collected, the system will provide feedback. If there is no feedback, the number of collected materials is generally no more than the specified number.
Even after placing the crafting table, we still consider them to be owned by the agent.
The complete process for crafting the "door" in Minecraft is as follows:
1. Use !collectBlocks(“oak_log”, 3) to collect at least three oak logs. Alternatively, spruce logs or birch logs can be used.
2. Convert logs into planks (“birch_planks”, “spruce_planks” or “oak_planks”). The command !craftRecipe(“oak_planks”, 4) will produce 16 planks. Note that 1 log is consumed for every 4 planks produced.
3. Use !craftRecipe(“crafting_table”, 1) to craft a “crafting_table”. Note that 4 planks are consumed for each crafting table produced.
4. After crafting a “crafting_table”, use the command !placeHere(“crafting_table”).
5. After crafting or finding a “crafting_table”, use !craftRecipe(“oak_door”, 1) or !craftRecipe(“birch_door”, 1) or !craftRecipe(“spruce_door”, 1) to craft 3 doors. Note that 6 planks are consumed for every 3 doors crafted."""

def url_to_base64(img_url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                base64_data = base64.b64encode(image_data.getvalue()).decode('utf-8')
                return f"data:image/png;base64,{base64_data}"
            else:
                print(f"Attempt {retries+1}/{max_retries}: Failed to download image from {img_url}, status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {retries+1}/{max_retries}: Error downloading image from {img_url}: {e}")
        
        sleep_time = (2 ** retries) + random.random()
        print(f"Retrying in {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        retries += 1
    
    print(f"Failed to download image after {max_retries} attempts: {img_url}")
    return None

def send_images_to_qwenvl(prompt, dialogue_history, image_urls):
    prompt = prompt + " The images are chronologically ordered, first-person perspective screenshots of the minecraft game. The dialogue history is as follows: " + dialogue_history + game_rule
    content = [{"type": "text", "text": prompt}]

    if isinstance(image_urls, str):
        image_urls = image_urls.split('\n\n') 

    successful_images = 0
    for img_url in image_urls:
        img_url = img_url.strip()
        if img_url:
            base64_img = url_to_base64(img_url)
            if base64_img:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": base64_img}
                })
                successful_images += 1
            else:
                print(f"Skipping image that could not be downloaded: {img_url}")
    
    if successful_images == 0 and len(image_urls) > 0:
        print("Warning: No images were successfully downloaded and converted to base64")
        return "ERROR: All image downloads failed"

    try:
        response = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[{"role": "user", "content": content}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling QwenVL API: {e}")
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

excel_path = "hinder-realtimeQA-door.xlsx"
df = pd.read_excel(excel_path)

with open("lmm/output/hinder_qwenvl_door_output.txt", "w", encoding="utf-8") as outfile:
    for index, row in df.iterrows():
        image_urls = row['image_url']
        dialogue_history = row['dialogue_history']

        questions = [
            {
                "character": row['character'],
                "target": "Jack",
                "options": row['Jack']
            },
            {
                "character": row['character'],
                "target": "Jane",
                "options": row['Jane']
            },
            {
                "character": row['character'],
                "target": "John",
                "options": row['John']
            },
        ]

        for q in questions:
            # prompt = f"You are {q['character']}. What materials or tools do you believe {q['target']} currently has? {q['options']} Please think step by step and choose one of the three options."
            prompt = f"You are {q['character']}. What materials or tools do you believe {q['target']} currently has? {q['options']} Please choose one of the three options and output only the letter."
            result = send_images_to_qwenvl(prompt, dialogue_history, image_urls)
            # option = extract_option(result)
            option = result
            # print(option + "\n------------------------------")
            print(option)
            if option:
                outfile.write(option + "\n")
                # outfile.write(option + "\n-------------------------------\n")

print("Results have been written to output.txt")