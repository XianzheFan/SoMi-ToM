import fs from 'fs';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env['OPENAI_API_KEY'],
});

async function main() {
  try {
    const chatCompletion = await openai.chat.completions.create({
      messages: [{ role: 'user', content: 'Hello, please introduce yourself.' }],
      model: 'gpt-3.5-turbo',
    });

    console.log(chatCompletion.choices[0].message);
  } catch (err) {
    console.error('Error with chat request:', err);
  }
}

async function streamResponse() {
  try {
    const stream = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: 'Tell a story about artificial intelligence.' }],
      stream: true,
    });

    for await (const chunk of stream) {
      process.stdout.write(chunk.choices[0]?.delta?.content || '');
    }
  } catch (err) {
    console.error('Error with streaming response:', err);
  }
}

async function uploadFile() {
  try {
    const fileStream = fs.createReadStream('input.jsonl');
    await openai.files.create({
      file: fileStream,
      purpose: 'fine-tune',
    });

    console.log('File uploaded successfully!');
  } catch (err) {
    console.error('Error uploading file:', err);
  }
}

async function handleErrors() {
  try {
    const result = await openai.chat.completions.create({
      model: 'non-existent-model',  // Incorrect model name
      messages: [{ role: 'user', content: 'Hello' }],
    });
  } catch (err) {
    if (err instanceof OpenAI.APIError) {
      console.log('HTTP Status Code:', err.status);
      console.log('Error Type:', err.name);
      console.log('Response Headers:', err.headers);  // Response headers
    } else {
      console.error('Other error:', err);
    }
  }
}

async function run() {
  await main();
  await streamResponse();
  await uploadFile();
  await handleErrors();
}

run();