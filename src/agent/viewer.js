import settings from '../../settings.js';
import prismarineViewer from 'prismarine-viewer';
import fs from 'fs';
import puppeteer from 'puppeteer';
import os from 'os';
import fetch from 'node-fetch';
import { getKey } from '../utils/keys.js';

const mineflayerViewer = prismarineViewer.mineflayer;

export function addViewer(bot, count_id) {
    if (settings.show_bot_views) {
        const port = 3000 + count_id;
        mineflayerViewer(bot, { port, firstPerson: true });
        console.log(`Viewer started at http://localhost:${port}`);
        const savePath = `screenshots/bot_${count_id}`;
        const screenshotInterval = settings.screenshotInterval || 30000; // ms
        captureScreenshotsWithApi(port, savePath, screenshotInterval);
    }
}

async function captureScreenshotsWithApi(port, savePath, interval = 30000) {
    if (!fs.existsSync(savePath)) {
        fs.mkdirSync(savePath, { recursive: true });
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
            headless: true
        });
        page = await browser.newPage();
        const url = `http://localhost:${port}`;
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 120000 });
        console.log(`Connected to ${url}. Starting screenshot capture.`);

        let capturing = false;

        setInterval(async () => {
            if (capturing) return;
            capturing = true;

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshotPath = `${savePath}/screenshot_${timestamp}.png`;
            try {
                await page.screenshot({ path: screenshotPath });
                console.log(`Screenshot saved: ${screenshotPath}`);
                
                const base64Image = await encodeImageToBase64(screenshotPath);
                const apiResponse = await callImageRecognitionApi(base64Image);
                console.log(`Image recognition result: ${JSON.stringify(apiResponse)}`);
            } catch (err) {
                console.error('Failed to capture screenshot or call API:', err);
            } finally {
                capturing = false;
            }
        }, interval);
    } catch (err) {
        console.error('Error during Puppeteer setup:', err);
        if (browser) await browser.close();
        return;
    }

    process.on('SIGINT', async () => {
        console.log('Shutting down Puppeteer...');
        if (browser) await browser.close();
        process.exit();
    });
}

async function encodeImageToBase64(imagePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(imagePath, (err, data) => {
            if (err) return reject(err);
            const base64Image = Buffer.from(data).toString('base64');
            resolve(base64Image);
        });
    });
}

async function callImageRecognitionApi(base64Image) {
    const apiEndpoint = 'https://api.openai.com/v1/chat/completions';
    const apiKey = getKey('OPENAI_API_KEY');

    const payload = {
        model: "gpt-4o-mini",
        messages: [
            {
                role: "user",
                content: [
                    {
                        type: "text",
                        text: "What is in this image?",
                    },
                    {
                        type: "image_url",
                        image_url: {
                            url: `data:image/jpeg;base64,${base64Image}`,
                        },
                    },
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