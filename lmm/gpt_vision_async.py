import openai
import os
import base64
from openai import AsyncOpenAI
import asyncio

openai.api_key = os.environ["OPENAI_API_KEY"]
client = AsyncOpenAI()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

async def main():
    async def openai_api_predict_async():
        response = await client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What are in these images?",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_1.jpg')}"},
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_2.jpg')}"},
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_3.jpg')}"},
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_4.jpg')}"},
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encode_image('extracted_frames/frame_5.jpg')}"},
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content
    response = await openai_api_predict_async()
    print(response)

asyncio.run(main())


# The images depict scenes from the game Minecraft. Here’s a brief overview of each:
# 1. **First Image**: Two characters, labeled Jane and John, are in a grassy area surrounded by trees and foliage.
# 2. **Second Image**: A character named Jack is seen from above, working amidst the trees. The dialogue suggests he is gathering resources, specifically oak logs.
# 3. **Third Image**: There's a focus on the ground with some items appearing nearby, likely items dropped from breaking blocks, and dialogue indicating crafting activities.
# 4. **Fourth Image**: John stands next to a crafting table while interacting with materials, indicating the crafting process is occurring.
# 5. **Fifth Image**: The three characters (John, Jane, and Jack) are discussing their crafting and resource sharing, with a crafting table also present.
# Overall, the images illustrate a collaborative gaming session focused on resource gathering and crafting within the Minecraft environment.