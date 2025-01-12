import google.generativeai as genai
import random
import time
import pandas as pd
import seaborn as sns

GOOGLE_API_KEY = "AIzaSyC-wiyh0yQOWQcmUTqiVRxzqZSxPkO0tHI"
genai.configure(api_key=GOOGLE_API_KEY)

print("Listing existing tuned models:")
for i, m in zip(range(5), genai.list_tuned_models()):
    print(m.name)

base_model = [
    m for m in genai.list_models()
    if "createTunedModel" in m.supported_generation_methods and
    "flash" in m.name][0]
print(f"Base model selected: {base_model.name}")

name = f'generate-num-{random.randint(0, 10000)}'

training_data = [
    {'text_input': '1', 'output': '2'},
    {'text_input': '3', 'output': '4'},
    {'text_input': '-3', 'output': '-2'},
    {'text_input': 'twenty two', 'output': 'twenty three'},
    {'text_input': 'two hundred', 'output': 'two hundred one'},
    {'text_input': 'ninety nine', 'output': 'one hundred'},
    {'text_input': '8', 'output': '9'},
    {'text_input': '-98', 'output': '-97'},
    {'text_input': '1,000', 'output': '1,001'},
    {'text_input': '10,100,000', 'output': '10,100,001'},
    {'text_input': 'thirteen', 'output': 'fourteen'},
    {'text_input': 'eighty', 'output': 'eighty one'},
    {'text_input': 'one', 'output': 'two'},
    {'text_input': 'three', 'output': 'four'},
    {'text_input': 'seven', 'output': 'eight'},
]

operation = genai.create_tuned_model(
    source_model=base_model.name,
    training_data=training_data,
    id=name,
    epoch_count=100,
    batch_size=4,
    learning_rate=0.001,
)

print(f"Training in progress for model: {name}")
for status in operation.wait_bar():
    time.sleep(30)

model = operation.result()
snapshots = pd.DataFrame(model.tuning_task.snapshots)
sns.lineplot(data=snapshots, x='epoch', y='mean_loss')

model = genai.GenerativeModel(model_name=f'tunedModels/{name}')

print("Evaluating the tuned model:")
test_inputs = ['55', '123455', 'four', 'quatre', 'III', '七']

for test_input in test_inputs:
    result = model.generate_content(test_input)
    print(f"Input: {test_input} -> Output: {result.text}")

genai.update_tuned_model(f'tunedModels/{name}', {"description": "This is my model."})

model = genai.get_tuned_model(f'tunedModels/{name}')
print(f"Updated description: {model.description}")

genai.delete_tuned_model(f'tunedModels/{name}')
try:
    m = genai.get_tuned_model(f'tunedModels/{name}')
    print(m)
except Exception as e:
    print(f"{type(e)}: {e}")
