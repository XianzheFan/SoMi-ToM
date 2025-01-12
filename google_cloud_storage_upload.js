import { Storage } from '@google-cloud/storage';

// Explicitly load service account credentials
const storage = new Storage({
    keyFilename: 'gen-lang-client-0978769179-b832acdace94.json',
});

const bucketName = 'minecraft_screenshot';
let filePath = 'extracted_frames/frame_1.jpg';

async function uploadFile(filePath) {
    const options = {
        destination: filePath,
        metadata: {
          contentType: 'image/jpeg', // Ensure the content type is set to image/jpeg for JPEG files
          contentDisposition: 'inline', // Ensure the file is displayed inline (not downloaded)
        },
    };
    await storage.bucket(bucketName).upload(filePath, options);
    console.log(`${filePath} uploaded to ${bucketName} as ${filePath}`);
}

uploadFile(filePath).catch(console.error);