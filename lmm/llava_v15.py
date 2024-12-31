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
    "yorickvp/llava-13b:80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb",
    input=input
):
    print(event, end="")

# export REPLICATE_API_TOKEN=r8_5UlzEjK8rkktYnqXteZK03Dr9A1R85t0VWeif

# The image is a computer-generated scene featuring a group of people standing in a grassy area. 
# There are four people in total, with one person standing near the center of the scene, another person on the left side, and two more people on the right side. They appear to be engaged in a conversation or interacting with each other.
# In the scene, there are also a couple of chests, one located near the center and the other towards the right side. Additionally, there are two trees in the background, one on the left side and the other on the right side of the image.