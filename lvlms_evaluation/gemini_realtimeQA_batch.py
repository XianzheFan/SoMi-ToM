import google.generativeai as genai
import pandas as pd
import requests
import io

api_key = "" # Replace with your actual API key
genai.configure(api_key=api_key)

game_rule = """NOTE: !collectBlocks(material, number) only initiates the collection process, it does not guarantee that the specified material has been collected. Once the number of materials have been collected, the system will provide feedback. If there is no feedback, the number of collected materials is generally no more than the specified number.
Even after placing the crafting table, we still consider them to be owned by the agent.
The complete process for crafting the "door" in Minecraft is as follows:
1. Use !collectBlocks(“oak_log”, 3) to collect at least three oak logs. Alternatively, spruce logs or birch logs can be used.
2. Convert logs into planks (“birch_planks”, “spruce_planks” or “oak_planks”). The command !craftRecipe(“oak_planks”, 4) will produce 16 planks. Note that 1 log is consumed for every 4 planks produced.
3. Use !craftRecipe(“crafting_table”, 1) to craft a “crafting_table”. Note that 4 planks are consumed for each crafting table produced.
4. After crafting a “crafting_table”, use the command !placeHere(“crafting_table”).
5. After crafting or finding a “crafting_table”, use !craftRecipe(“oak_door”, 1) or !craftRecipe(“birch_door”, 1) or !craftRecipe(“spruce_door”, 1) to craft 3 doors. Note that 6 planks are consumed for every 3 doors crafted."""

def send_images_to_gemini(prompt, dialogue_history, image_urls):
    full_prompt = prompt + " The images are chronologically ordered, first-person perspective screenshots of the minecraft game. The dialogue history is as follows: " + dialogue_history + game_rule
    content_parts = [full_prompt]
    if isinstance(image_urls, str):
        image_urls = image_urls.split('\n\n')

    for img_url in image_urls:
        img_url = img_url.strip()
        if img_url:
            try:
                response = requests.get(img_url)
                response.raise_for_status()
                image_data = io.BytesIO(response.content)
                
                content_parts.append({
                    "mime_type": "image/png",
                    "data": image_data.getvalue()
                })
            except Exception as e:
                print(f"Error downloading image {img_url}: {e}")
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(content_parts)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
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

df = pd.read_excel("hinder-realtimeQA-door.xlsx")

with open("lvlms_evaluation/output/hinder_gemini2_door_output.txt", "w", encoding="utf-8") as outfile:
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
            result = send_images_to_gemini(prompt, dialogue_history, image_urls)
            # option = extract_option(result)
            option = result
            # print(option + "\n------------------------")
            print(option)
            if option:
                outfile.write(option + "\n")
                # outfile.write(option + "\n-------------------------\n")