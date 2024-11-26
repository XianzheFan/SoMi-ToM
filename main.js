import WebSocket from 'ws';
import { AgentProcess } from './src/process/agent-process.js';
import settings from './settings.js';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import { createMindServer } from './src/server/mind_server.js';

function parseArguments() {
    return yargs(hideBin(process.argv))
        .option('profiles', {
            type: 'array',
            describe: 'List of agent profile paths',
        })
        .help()
        .alias('help', 'h')
        .parse();
}

function getProfiles(args) {
    return args.profiles || settings.profiles;
}

async function startWebSocketClient() {
    const wsUri = 'ws://localhost:8000/ws/test_client';
    const ws = new WebSocket(wsUri);

    ws.on('open', () => {
        console.log('WebSocket client connected to server');
        ws.send(JSON.stringify({ message: 'Hello from main.js!' }));
    });

    ws.on('message', (message) => {
        console.log(`Message from server: ${message}`);
        handleServerMessage(ws, message);
    });

    ws.on('error', (error) => {
        console.error(`WebSocket error: ${error}`);
    });

    ws.on('close', () => {
        console.log('WebSocket connection closed');
    });
}

function handleServerMessage(ws, message) {
    try {
        // Parse the message sent by the server
        const parsedMessage = JSON.parse(message);
        console.log('Received from server:', parsedMessage);

        if (parsedMessage.action === 'start_process') {
            // Start the proxy process based on the server's request
            const profileIndex = parsedMessage.profile_index;
            const profiles = getProfiles(parseArguments());
            const { load_memory, init_message } = settings;

            if (profileIndex >= 0 && profileIndex < profiles.length) {
                console.log(`Starting process for profile index: ${profileIndex}`);
                const agent = new AgentProcess();
                agent.start(profiles[profileIndex], load_memory, init_message, profileIndex);

                const response = JSON.stringify({
                    status: 'success',
                    profile_index: profileIndex,
                    message: 'Process started successfully',
                    timestamp: new Date().toISOString()
                });
                ws.send(response);
            } else {
                const errorResponse = JSON.stringify({
                    status: 'error',
                    profile_index: profileIndex,
                    message: 'Invalid profile index',
                    timestamp: new Date().toISOString()
                });
                ws.send(errorResponse);
                console.warn(`Invalid profile index received: ${profileIndex}`);
            }
        } else {
            console.warn('Unknown action received:', parsedMessage.action);
        }
    } catch (error) {
        console.error('Error handling server message:', error);

        const errorResponse = JSON.stringify({
            status: 'error',
            message: 'Failed to handle server message',
            timestamp: new Date().toISOString()
        });
        ws.send(errorResponse);
    }
}

async function main() {
    if (settings.host_mindserver) {
        const mindServer = createMindServer();
    }

    await startWebSocketClient();

    const args = parseArguments();
    const profiles = getProfiles(args);
    console.log(profiles);

    const { load_memory, init_message } = settings;
    for (let i = 0; i < profiles.length; i++) {
        const agent = new AgentProcess();
        agent.start(profiles[i], load_memory, init_message, i);
    }
}

try {
    main();
} catch (error) {
    console.error('An error occurred:', error);
    process.exit(1);
}