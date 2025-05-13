import { GoogleAIFileManager, FileState } from "@google/generative-ai/server";
import { GoogleGenerativeAI } from "@google/generative-ai";
import * as fs from 'fs';
import * as path from 'path';
import XLSX from 'xlsx';

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
  const responseText = result.response.text();
  return responseText;
}

async function processExcelFile(excelPath, videoBasePath = null, outputFile = "lvlms_evaluation/output_videoqa/gemini2_cot_videoqa.txt") {
  try {
    const workbook = XLSX.readFile(excelPath);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    const outputDir = path.dirname(outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const outputStream = fs.createWriteStream(outputFile);
    outputStream.write("Gemini 2 Video QA Results\n");
    outputStream.write("======================\n\n");
    
    for (const row of data) {
      const name = row[0]; // First column contains the name
      const videoFile = row[1]; // Second column contains the video filename
      
      const videoPath = videoBasePath ? path.join(videoBasePath, videoFile) : videoFile;
      
      const header = `\n--- Processing video for ${name} (${videoFile}) ---\n`;
      outputStream.write(header);
      console.log(header);
      
      try {
        const video = await uploadVideo(videoPath, "video/mp4", name);
        const fileUri = await waitForFileProcessing(video.name);
        
        // Process each question (columns 3-10)
        for (let i = 2; i < 10 && i < row.length; i++) {
          if (row[i] && row[i] !== "") {
            const question = row[i];
            // const fullQuestion = `${question} Please choose one of the three options and output only the letter.`;
            const fullQuestion = `${question} Please think step by step and choose one of the three options.`;
            
            const result = await askQuestionAboutVideo(fileUri, fullQuestion);
            
            outputStream.write(result);
            console.log(result);
            outputStream.write("\n------------------\n");
            console.log("\n------------------\n");
          }
        }
      } catch (error) {
        const errorMsg = `Error processing video ${videoFile}: ${error}\n`;
        outputStream.write(errorMsg);
        console.error(errorMsg);
      }
    }
    
    outputStream.end();
    console.log(`Results saved to ${outputFile}`);
  } catch (error) {
    console.error("Error processing Excel file:", error);
  }
}

async function main() {
  try {
    const excelPath = "hinder-videoqa.xlsx";
    const videoBasePath = "Videos/";
    
    await processExcelFile(excelPath, videoBasePath);
  } catch (error) {
    console.error("Error:", error);
  }
}

main();