import settings from '../../settings.js';
import prismarineViewer from 'prismarine-viewer';
import fs from 'fs';
import puppeteer from 'puppeteer';
import os from 'os';
const mineflayerViewer = prismarineViewer.mineflayer;

export function addViewer(bot, count_id) {
    if (settings.show_bot_views) {
        const port = 3000 + count_id;
        mineflayerViewer(bot, { port, firstPerson: true });
        console.log(`Viewer started at http://localhost:${port}`);
        const savePath = `screenshots/bot_${count_id}`;
        const screenshotInterval = settings.screenshotInterval || 20000; // ms
        captureScreenshots(port, savePath, screenshotInterval);
    }
}

async function captureScreenshots(port, savePath, interval = 20000) {
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
            } catch (err) {
                console.error('Failed to capture screenshot:', err);
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