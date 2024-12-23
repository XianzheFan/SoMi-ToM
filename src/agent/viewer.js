import settings from '../../settings.js';
import prismarineViewer from 'prismarine-viewer';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer';
import os from 'os';
import fetch from 'node-fetch';
import { getKey } from '../utils/keys.js';
import { exec } from 'child_process';

const mineflayerViewer = prismarineViewer.mineflayer;

export function addViewer(bot, count_id, name) {
    if (settings.show_bot_views) {
        const port = 3000 + count_id;
        mineflayerViewer(bot, { port, firstPerson: true });
        console.log(`Viewer started at http://localhost:${port}`);
        const savePath = `screenshots/${name}`;
        const tempPath = `temp_screenshots/${name}`;
        const screenshotInterval = 2000; // 2 seconds for video
        const saveInterval = 30000; // 30 seconds for saving
        captureScreenshotsWithApi(port, savePath, tempPath, screenshotInterval, saveInterval);
    }
}

let isRecording = true;

async function captureScreenshotsWithApi(port, savePath, tempPath, screenshotInterval = 2000, saveInterval = 30000) {
    if (!fs.existsSync(savePath)) {
        fs.mkdirSync(savePath, { recursive: true });
    }
    if (!fs.existsSync(tempPath)) {
        fs.mkdirSync(tempPath, { recursive: true, mode: 0o777 });
    }

    let browser;
    let page;
    const platform = os.platform();
    let chromePath;
    if (platform === 'win32') {
        chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    } else if (platform === 'darwin') {
        chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    } else if (platform === 'linux') {
        chromePath = '/usr/bin/google-chrome';
    } else {
        console.error(`Unsupported platform: ${platform}`);
        return;
    }

    try {
        browser = await puppeteer.launch({
            executablePath: chromePath,
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        page = await browser.newPage();
        const url = `http://localhost:${port}`;
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 120000 });
        console.log(`Connected to ${url}. Starting screenshot capture.`);

        let lastSaveTime = 0;

        const screenshotIntervalId = setInterval(async () => {
            if (!isRecording) {
                clearInterval(screenshotIntervalId);
                await generateVideoFromFileList(`${tempPath}/file_list.txt`, `${savePath}/output_video.mp4`);
                if (browser) await browser.close();
                return;
            }

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const tempScreenshotPath = path.join(tempPath, `screenshot_${timestamp}.png`);
            const saveScreenshotPath = path.join(savePath, `screenshot_${timestamp}.png`);

            try {
                await page.screenshot({ path: tempScreenshotPath });
                // console.log(`Temporary screenshot saved: ${tempScreenshotPath}`);

                const currentTime = Date.now();
                if (currentTime - lastSaveTime >= saveInterval) {
                    fs.copyFileSync(tempScreenshotPath, saveScreenshotPath);
                    lastSaveTime = currentTime;
                    console.log(`Saved screenshot for record: ${saveScreenshotPath}`);
                }
            } catch (err) {
                // console.error('Failed to capture screenshot:', err);
            }
        }, screenshotInterval);
    } catch (err) {
        console.error('Error during Puppeteer setup:', err);
        if (browser) await browser.close();
    }
}

export function stopRecording(tempPath, savePath) {
    isRecording = false;
    setTimeout(() => {
        console.log('Stopping recording and generating video...');
        const listFile = path.join(tempPath, 'file_list.txt');
        generateFileList(tempPath, listFile);
        generateVideoFromFileList(listFile, `${savePath}/output_video.mp4`);
    }, 1000); // Ensure all screenshot tasks are completed
}

function generateVideoFromFileList(listFile, outputVideoPath) {
    return new Promise((resolve, reject) => {
        const command = `ffmpeg -f concat -safe 0 -i ${listFile} -r 1 -c:v libx264 -pix_fmt yuv420p ${outputVideoPath}`; // 1 fps

        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error generating video: ${stderr}`);
                reject(error);
            } else {
                console.log(`Video generated successfully at: ${outputVideoPath}`);
                resolve();
            }
        });
    }).catch(err => {
        console.error('Unhandled error in video generation:', err);
    });
}

export async function encodeImageToBase64(imagePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(imagePath, (err, data) => {
            if (err) return reject(err);
            const base64Image = Buffer.from(data).toString('base64');
            resolve(base64Image);
        });
    });
}

function generateFileList(directory, listFile) {
    const files = fs.readdirSync(directory)
        .filter(file => file.endsWith('.png'))
        .sort(); // Ensure the files are sorted by name
    const fileContent = files
        .map(file => `file '${path.resolve(directory, file).replace(/\\/g, '/')}'`)
        .join('\n');
    fs.writeFileSync(listFile, fileContent);
    console.log(`Generated file list: ${listFile}`);
}

export async function callImageRecognitionApi(base64Image) {
    const apiEndpoint = 'https://api.openai.com/v1/chat/completions';
    const apiKey = getKey('OPENAI_API_KEY');

    const payload = {
        model: "gpt-4o-mini",
        messages: [
            {
                role: "user",
                content: [
                    { type: "text", text: "What is in this image?", },
                    { type: "image_url", image_url: { url: `data:image/jpeg;base64,${base64Image}`, }, },
                ],
            },
        ],
    };

    const headers = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
    };

    try {
        const response = await fetch(apiEndpoint, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        const data = await response.json();
        return data;
    } catch (err) {
        console.error('Error calling image recognition API:', err);
        throw err;
    }
}