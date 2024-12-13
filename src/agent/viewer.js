import settings from '../../settings.js';
import prismarineViewer from 'prismarine-viewer';
import fs from 'fs';
import puppeteer from 'puppeteer';
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
    try {
        try {
            browser = await puppeteer.launch({
                executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                headless: true
            });            
            page = await browser.newPage();
            const url = `http://localhost:${port}`;
            await page.goto(url, { waitUntil: 'networkidle2', timeout: 120000 });
            console.log(`Connected to ${url}. Starting screenshot capture.`);
        } catch (err) {
            console.error('Error during Puppeteer setup:', err.message || err, err.stack || '');
            return;
        }

        setInterval(async () => {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshotPath = `${savePath}/screenshot_${timestamp}.png`;
            try {
                await page.screenshot({ path: screenshotPath });
                console.log(`Screenshot saved: ${screenshotPath}`);
            } catch (err) {
                console.error('Failed to capture screenshot:', err);
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