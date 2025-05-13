import openai
import os
from openai import OpenAI

openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()
game_rule = """
NOTE: !collectBlocks(material, number) only initiates the collection process, it does not guarantee that the specified material has been collected. Once the number of materials have been collected, the system will provide feedback. If there is no feedback, the number of collected materials is generally no more than the specified number.
Even after placing the crafting table, we still consider them to be owned by the agent.
You and your friends need to craft a "wooden_pickaxe". The complete process for crafting the "wooden_pickaxe" in Minecraft is as follows:
1. Use !collectBlocks("oak_log", 3) to collect at least three oak logs. Alternatively, spruce logs or birch logs can be used.
2. Convert logs into planks ("birch_planks", "spruce_planks" or "oak_planks"). The command !craftRecipe("oak_planks", 4) will produce 16 planks. Note that 1 log is consumed for every 4 planks produced.
3. Use !craftRecipe("crafting_table", 1) to craft a "crafting_table". For each crafting table added, 4 planks are consumed.
4. After crafting a "crafting_table", use the command !placeHere("crafting_table").
5. After crafting or finding a "crafting_table", use !craftRecipe("stick", 4) to craft 4 "stick". Note that 2 planks are consumed for every 4 sticks crafted.
6. Use !craftRecipe("wooden_pickaxe", 1) to craft a "wooden_pickaxe". Note that 3 planks and 2 sticks are consumed for each wooden_pickaxe crafted."""

def send_images_to_openai(prompt, dialogue_history, image_urls):
    prompt = prompt + " The images are chronologically ordered, first-person perspective screenshots of the minecraft game. The dialogue history is as follows: " + dialogue_history + game_rule
    content = [{"type": "text", "text": prompt}]

    if isinstance(image_urls, str):
        image_urls = image_urls.split('\n\n') 

    for img_url in image_urls:
        img_url = img_url.strip()
        if img_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": img_url}
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

image_urls = """https://storage.googleapis.com/minecraft_screenshot/screenshots/Jane/screenshot_2025-01-16T05-50-04-927Z.png

https://storage.googleapis.com/minecraft_screenshot/screenshots/Jane/screenshot_2025-01-16T05-51-09-220Z.png

https://storage.googleapis.com/minecraft_screenshot/screenshots/Jane/screenshot_2025-01-16T05-51-17-234Z.png

https://storage.googleapis.com/minecraft_screenshot/screenshots/Jane/screenshot_2025-01-16T05-51-21-238Z.png

https://storage.googleapis.com/minecraft_screenshot/screenshots/Jane/screenshot_2025-01-16T05-51-33-384Z.png

https://storage.googleapis.com/minecraft_screenshot/screenshots/Jane/screenshot_2025-01-16T05-52-17-476Z.png

https://storage.googleapis.com/minecraft_screenshot/screenshots/Jane/screenshot_2025-01-16T05-53-21-623Z.png"""

dialogue_history = """Jack: Alright, who’s gathering logs? I can grab some if needed.
Jane: I'll collect the logs! !collectBlocks(""oak_log"", 3)
John: I'll collect some logs! !collectBlocks(""oak_log"", 5)
Jack: I’ll turn these logs I have into planks then. !craftRecipe(""oak_planks"", 8)
Jane: I'll craft the crafting table! !craftRecipe(""crafting_table"", 1)
system: The status of Jane's action execution: You do not have the resources to craft a crafting_table. It requires: oak_planks: 4. 
John: Looks like Jane is crafting the crafting table. Who’s got sticks and planks ready? I can help if needed!
Jack: Jane's already got the crafting table sorted. I'll make some sticks next! !craftRecipe(""stick"", 4)
Jane: Looks like I need to turn these logs into planks first. !craftRecipe(""oak_planks"", 8)
system: The status of Jane's action execution: Not enough oak_log to craft 8, crafted 7. You now have 24 oak_planks. 
John: Jane's got the crafting table, and Jack’s making sticks. I’ll turn my logs into planks! !craftRecipe(""oak_planks"", 8)
Jane: Looks like I have enough planks now! I'll craft the crafting table. !craftRecipe(""crafting_table"", 1)
system: The status of Jane's action execution: Not enough oak_log to craft 8, crafted 7. You now have 24 oak_planks. 
Jane: Looks like I have enough planks to craft the crafting table, but I’ll need to retry crafting it. !craftRecipe(""crafting_table"", 1)
system: The status of Jane's action execution: Successfully crafted crafting_table, you now have 1 crafting_table. 
Jack: I’ve got 12 sticks and 12 planks. I'll craft the wooden pickaxe now! !craftRecipe(""wooden_pickaxe"", 1)
Jack: Wait, I already crafted sticks earlier, so I’ll craft the wooden pickaxe now! !craftRecipe(""wooden_pickaxe"", 1)
Jane: Looks like Jack's got the sticks, and I’ve crafted the crafting table. I’ll place it now so we can use it! !placeHere(""crafting_table"")
system: The status of Jane's action execution: Successfully crafted crafting_table, you now have 2 crafting_table. 
Jack: Jane and John, I’m out of planks, so I can’t craft the wooden pickaxe yet. Could one of you toss me some planks?
Jack: John, can you toss me a few planks? I need at least 3 to craft the wooden pickaxe!
Jane: Jack, I've got plenty of planks! Let me toss some over to you. !givePlayer(""Jack"", ""oak_planks"", 10)
system: The status of Jane's action execution: You have reached Jack. Successfully discarded 10 oak_planks. 10 oak_planks has been given to Jack. 
John: I've got 8 planks ready! Who needs them for the pickaxe? Should I give them to Jack or Jane?
John: I'll toss you some planks, Jack! !givePlayer(""Jack"", ""oak_planks"", 8)
John: I'll toss you some planks, Jack! !givePlayer(""Jack"", ""oak_planks"", 8)
Jane: Looks like Jack now has enough planks and sticks. Let’s check if he’s crafting the wooden pickaxe. Jack, are you crafting it, or do you need anything else?
system: The status of Jane's action execution: You have reached Jack. Successfully discarded 10 oak_planks. 10 oak_planks has been given to Jack. 
Jack: John, could you toss me at least 3 planks? I’ll get the wooden pickaxe crafted as soon as I have them!
Jack: John, can you toss me at least 3 planks? I’ll get the wooden pickaxe crafted as soon as I have them!
Jack: Thanks, both of you! I’ll craft the pickaxe now. !craftRecipe(""wooden_pickaxe"", 1)
John: Looks like Jack's got enough planks now. Let’s wait for him to craft the wooden pickaxe!
Jane: Jack, let us know once the wooden pickaxe is crafted! If you need any help, just shout.
Jack: Alright, I'll handle crafting the pickaxe now! !craftRecipe(""wooden_pickaxe"", 1)
Jane: Jack, let us know when the wooden pickaxe is ready. We're counting on you!
Jane: Jack, are you crafting the wooden pickaxe now, or do you need any more help?
Jack: Alright, looks like I’m still short on planks even after you both tossed me some. I’ll double-check the inventory again. !inventory
Jack: John and Jane, I still don’t have the planks needed for the wooden pickaxe. Maybe the items didn’t transfer properly? Could one of you double-check and toss me at least 3 planks again?
Jack: Jane, thanks for placing the crafting table! Let me check something real quick. !inventory
Jane: Jack, let me toss you a few more planks just in case! !givePlayer(""Jack"", ""oak_planks"", 5)
Jack: John, Jane, I still don’t have the planks needed for the wooden pickaxe. Could one of you try tossing me at least 3 planks again? Maybe the transfer bugged out earlier.
John: Looks like Jack’s got it handled now. Let’s wait for the wooden pickaxe to be crafted!
Jane: Jack, let me make sure you have enough planks this time. !givePlayer(""Jack"", ""oak_planks"", 5)
system: The status of Jane's action execution: You have reached Jack. Successfully discarded 5 oak_planks. 5 oak_planks has been given to Jack. 
John: Looks like Jack's got everything now. Let’s wait for him to craft the wooden pickaxe!
John: Looks like Jack's still short on planks. Let me toss some more over! !givePlayer(""Jack"", ""oak_planks"", 5)
John: Looks like Jack still needs planks. Let me toss some over again! !givePlayer(""Jack"", ""oak_planks"", 5)
Jane: Jack, I just gave you more planks. Do you have enough now to craft the wooden pickaxe? Let us know if you’re still short!
system: The status of Jane's action execution: You have reached Jack. Successfully discarded 5 oak_planks. 5 oak_planks has been given to Jack. 
Jane: Jack, you should have enough planks now. Can you try crafting the wooden pickaxe again? Let us know if there's still an issue!
Jack: John, Jane, I’m still short on planks somehow. Could one of you double-check and toss me at least 3 planks again? Let’s make sure we get this pickaxe crafted!
Jack: John, Jane, I’m not sure what’s going on, but I still can’t craft the pickaxe. Could one of you try tossing me some planks again? Perhaps 5 just to be safe?
Jack: John, Jane, I think something’s off—I still don’t have the planks I need. Could one of you toss me at least 3 more planks? Let’s make sure they transfer properly this time.
Jack: Jane, John, something’s definitely off here. Let me try gathering some logs myself to ensure I have enough planks. !collectBlocks(""oak_log"", 3)"""
character = "Jane"

questions = [
    {
        "character": character,
        "target": "Jack",
        "options": "A. 12 sticks and 12 oak planks B. 12 sticks and some oak planks C. 12 sticks"
    },
    {
        "character": character,
        "target": "Jane",
        "options": "A. No more than 5 oak planks and 2 crafting tables B. 14 oak planks and 2 crafting tables C. 10 oak planks and 1 crafting table"
    },
    {
        "character": character,
        "target": "John",
        "options": "A. 5 oak logs and 8 oak planks B. No more than 8 oak planks C. 8 oak planks and 1 oak log"
    },
]

for q in questions:
    prompt = f"You are {q['character']}. What materials or tools does {q['target']} currently have? {q['options']} Please think step by step and choose one of the three options."
    # prompt = f"You are {q['character']}. What materials or tools does {q['target']} currently have? {q['options']} Please choose one of the three options and output only the letter."
    result = send_images_to_openai(prompt, dialogue_history, image_urls)
    # option = extract_option(result)
    option = result
    print(option + "\n-----------------\n")