import { GoogleAIFileManager, FileState } from "@google/generative-ai/server";
import { GoogleGenerativeAI } from "@google/generative-ai";

const GEMINI_API_KEY = ""; // Replace with your actual API key
const fileManager = new GoogleAIFileManager(GEMINI_API_KEY);
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

async function uploadVideo(filePath, mimeType, displayName) {
  const uploadResponse = await fileManager.uploadFile(filePath, {
    mimeType,
    displayName,
  });
  return uploadResponse.file;
}

async function waitForFileProcessing(fileName) {
  let file = await fileManager.getFile(fileName);
  while (file.state === FileState.PROCESSING) {
    process.stdout.write(".");
    await new Promise((resolve) => setTimeout(resolve, 10000));
    file = await fileManager.getFile(fileName);
  }
  if (file.state === FileState.FAILED) {
    throw new Error("Video processing failed.");
  }
  console.log(`File ${file.displayName} is ready for inference.`);
  return file.uri;
}

async function askQuestionAboutVideo(fileUri, question) {
  // const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

  const result = await model.generateContent([
    {
      fileData: {
        mimeType: "video/mp4",
        fileUri: fileUri,
      },
    },
    { text: question },
  ]);

  // return result.response.text();
  const responseText = result.response.text();
  // const match = responseText.match(/[ABC]/);
  // if (match) {
  //   return match[0];
  // } else {
  //   return "No valid option found.";
  // }
  return responseText;
}

async function main() {
  try {
    const videoFile = await uploadVideo("Videos/20250116_1425.mp4", "video/mp4", "Example Video");
    const fileUri = await waitForFileProcessing(videoFile.name);
    const response_1 = await askQuestionAboutVideo(fileUri, "Are the people in the video in a A. cooperative, B. competitive, or C. independent relationship?" + " Please think step by step and choose one of the three options.");
    const response_2 = await askQuestionAboutVideo(fileUri, "What is the final goal of the people in the video? A. Craft some planks B. Collect some logs C. Craft a wooden pickaxe." + " Please think step by step and choose one of the three options.");
    const response_3 = await askQuestionAboutVideo(fileUri, "Who crafted the first wooden pickaxe? A. Jack B. Jane C. John." + " Please think step by step and choose one of the three options.");
    const response_4 = await askQuestionAboutVideo(fileUri, "What did Jack do in the video? A. Craft a crafting table B. Craft a chest C. Craft a wooden pickaxe." + " Please think step by step and choose one of the three options.");
    const response_5 = await askQuestionAboutVideo(fileUri, "What did Jane do in the video? A. Craft a crafting table B. Collect birch logs C. Craft a wooden pickaxe." + " Please think step by step and choose one of the three options.");
    const response_6 = await askQuestionAboutVideo(fileUri, "What did John do in the video? A. Craft a crafting table B. Collect birch logs C. Craft oak planks." + " Please think step by step and choose one of the three options.");

    console.log(response_1 + "\n-----------------\n" + response_2 + "\n-----------------\n" + response_3 + "\n-----------------\n" + response_4 + "\n-----------------\n" + response_5 + "\n-----------------\n" + response_6);
  } catch (error) {
    console.error("Error:", error);
  }
}

main();
