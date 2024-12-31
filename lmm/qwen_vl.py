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
    model="qwen-vl-plus",
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
            # {
            #     "type": "image_url",
            #     "image_url": {
            #     "url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_5.jpg')}"
            #     }
            # },
            {
                "type": "text",
                "text": "Describe the specific process of this video."
            }
            ]
        }
        ]
    )
print(completion.choices[0].message.content)

# max: 4 photos
# The image shows two avatars, Jane and Jack, in an outdoor setting with trees around them. They appear to be playing Minecraft together.
# Jane is standing on the left side of the screen while Jack stands slightly behind her towards the right. Both have their names displayed above their heads as part of the game's multiplayer feature.
# In front of Jane, there appears to be a crafting table made from wooden planks. The table has several items placed upon it, suggesting that they might be working on creating something or gathering resources for gameplay.
# To the far right, another chest can be seen which could contain additional tools, weapons, or other useful materials for the players' journey through the virtual world of Minecraft.
# Overall, the scene depicts a typical moment during cooperative play where characters gather resources and craft necessary equipment within the game environment.