import openai
openai.api_key = "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"

completion = openai.chat.completions.create(
    model="gpt-4o-2024-11-20",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.choices[0].message.content)