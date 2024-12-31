import replicate

image_1 = open("extracted_frames/frame_1.jpg", "rb")
image_2 = open("extracted_frames/frame_2.jpg", "rb")
image_3 = open("extracted_frames/frame_3.jpg", "rb")
image_4 = open("extracted_frames/frame_4.jpg", "rb")
image_5 = open("extracted_frames/frame_5.jpg", "rb")

input = {
    "image": image_1,
    "image": image_2,
    "image": image_3,
    "image": image_4,
    "image": image_5,
    "prompt": "Describe the contents of these images."
}

for event in replicate.stream(
    "yorickvp/llava-v1.6-vicuna-13b:0603dec596080fa084e26f0ae6d605fc5788ed2b1a0358cd25010619487eae63",
    input=input
):
    print(event, end="")

# export REPLICATE_API_TOKEN=r8_5UlzEjK8rkktYnqXteZK03Dr9A1R85t0VWeif

# The image is a screenshot from a video game, specifically from the game "Minecraft." It shows a three-dimensional, blocky, pixelated environment that is characteristic of the game's visual style. In the foreground, there are two characters standing on grass. 
# The character on the left is wearing a green shirt and has a brown hat, while the character on the right is wearing a yellow shirt and has dark hair. Both characters appear to be looking towards the camera.
# In the background, there are trees with green leaves and a clear blue sky. The environment suggests a peaceful, natural setting within the game.
# At the bottom of the image, there is a chat overlay with text that reads: "Jack: Sounds good Jane! Craft those planks and share then when you're ready, and Jane, sounds like Jane is crafting too! Once Jack's chest is ready, we all set to place them then. 
# Let me know if I need to help with anything." The text indicates that the characters are engaged in a conversation, possibly discussing gameplay or tasks within the game.
# The overall style of the image is consistent with the game's aesthetic, which is known for its simplicity and focus on creativity and exploration.