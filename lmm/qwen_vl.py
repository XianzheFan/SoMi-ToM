from openai import OpenAI
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

base64_image = encode_image('extracted_frames/frame_1.jpg')
client = OpenAI(
    api_key="sk-c8d3783668b64312bf8811607dfb1b92",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-vl-max-latest",
    messages=[
        {
            "role": "user",
            "content": [
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_1.jpg')}"
                }
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_2.jpg')}"
                }
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_3.jpg')}"
                }
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_4.jpg')}"
                }
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_5.jpg')}"
                }
            },
            {
                "type": "text",
                "text": "Describe the specific process of this video."
            }
            ]
        }
        ]
    )
print(completion.choices[0].message.content)


# The video depicts a collaborative process among three players named Jack, John, and Jane in a Minecraft environment. Here is the specific sequence of events:
# 1. **Initial Gathering (Figure 1)**:
#    - The scene opens with Jack, John, and Jane standing in a forest area.
#    - They are discussing their plan to gather resources.
# 2. **Resource Collection (Figure 2)**:
#    - Jack is shown collecting oak logs from a tree.
#    - He uses the command `collectBlocks("oak_log", 1)` to collect one oak log.
#    - John and Jane are also present, and they discuss splitting the planks and crafting chests.
# 3. **Crafting Table Creation (Figure 3)**:
#    - Jane crafts a crafting table using the command `craftRecipe("crafting_table", 1)`.
#    - She successfully creates the crafting table and shares this information with Jack and John.
#    - Jack then uses the command `givePlayer("John", "oak_planks", 8)` to give John the necessary oak planks for crafting.
# 4. **Chest Crafting (Figure 4)**:
#    - John finds the crafting table at coordinates (3, 70, 11).
#    - He successfully crafts a chest using the oak planks.
#    - Jack attempts to craft a chest but lacks the required oak planks.
#    - John picks up an item, possibly another resource needed for further crafting.
# 5. **Final Collaboration (Figure 5)**:
#    - All three players are now gathered around the crafted chest.
#    - They discuss sharing the planks and finalizing their plans.
#    - Jack and John confirm that once the chest is ready, they will place it together.
# Throughout the video, the players work together efficiently, communicating and utilizing commands to achieve their goals in the Minecraft environment.