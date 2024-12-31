import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyC-wiyh0yQOWQcmUTqiVRxzqZSxPkO0tHI"
genai.configure(api_key=GOOGLE_API_KEY)

def upload_image(image_path):
    sample_file = genai.upload_file(path=image_path, display_name=image_path.split("/")[-1])
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    return sample_file

def upload_and_generate_multiple_images(image_paths, prompt):
    uploaded_files = []
    for image_path in image_paths:
        uploaded_file = upload_image(image_path)
        uploaded_files.append(uploaded_file)

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    inputs = []
    for uploaded_file in uploaded_files:
        inputs.append(uploaded_file)
    inputs.append(prompt)
    response = model.generate_content(inputs)
    
    return response.text

image_paths = [
    'extracted_frames/frame_1.jpg',
    'extracted_frames/frame_2.jpg',
    'extracted_frames/frame_3.jpg',
    'extracted_frames/frame_4.jpg',
    'extracted_frames/frame_5.jpg'
]

prompt = "Describe the contents of these images."

response_text = upload_and_generate_multiple_images(image_paths, prompt)
print(response_text)


# The images show a sequence of screenshots from a Minecraft game, likely demonstrating a collaborative building effort between three players named John, Jane, and Jack.
# * **Image 1:** Shows the three players in a forested area. John and Jane are visible, while Jack is partially obscured by leaves. The names of the players are displayed above their respective characters.
# * **Image 2:** Jack's first-person perspective as he gathers wood. A chat log at the bottom left indicates instructions or comments, likely from a code interpreter or plugin guiding their actions. It mentions collecting oak logs for planks.
# * **Image 3:** Shows Jane's perspective close to the ground, near a newly placed crafting table and some dirt blocks. The chat log documents actions taken, like crafting the table.
# * **Image 4:** John stands next to the crafting table. The chat log shows that John found the crafting table and attempts to craft a chest. However, the attempt fails due to insufficient resources (oak planks).
# * **Image 5:** The three players gather around the crafting table. The chat log discusses sharing planks and further crafting plans. It indicates a coordinated effort where they divide tasks like gathering wood and crafting items.
# The screenshots showcase a modded or plugin-enhanced Minecraft experience, where actions are logged and possibly guided by external code. The players are focused on basic early-game tasks, gathering resources and crafting essential items like a crafting table and a chest.