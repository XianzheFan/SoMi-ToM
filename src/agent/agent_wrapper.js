import { Agent } from './agent.js';
import WebSocket from 'ws';

export class AgentWrapper {
    constructor(profile_fp, websocketUrl) {
        this.agent = new Agent();
        this.websocketUrl = websocketUrl;
        this.websocket = null;
        this.profile_fp = profile_fp;
    }

    async initialize(load_mem = false, init_message = null, count_id = 0) {
        console.log('Initializing agent wrapper...');
        await this.agent.start(this.profile_fp, load_mem, init_message, count_id);

        if (this.websocketUrl) {
            this.connectWebSocket();
        }
    }

    connectWebSocket() {
        console.log(`Connecting to WebSocket server at ${this.websocketUrl}...`);
        this.websocket = new WebSocket(this.websocketUrl);

        this.websocket.on('open', () => {
            console.log('WebSocket connection established.');
            this.websocket.send(JSON.stringify({ type: 'status', message: 'Agent connected' }));
        });

        this.websocket.on('message', async (data) => {
            try {
                const message = JSON.parse(data);
                console.log('Received WebSocket message:', message);
        
                if (message.type === 'command' && message.command) {
                    console.log('Executing command:', message.command);
                    await this.agent.handleMessage('system', message.command);
                } else if (message.type === 'interrupt') {
                    console.log('Interrupt command received.');
                    this.agent.requestInterrupt();
                } else if (message.type === 'response') {
                    console.log('Response from server:', message.message);
                } else {
                    console.warn('Unknown message type:', message.type);
                }
            } catch (error) {
                console.error('Error handling WebSocket message:', error);
            }
        });        

        this.websocket.on('close', () => {
            console.log('WebSocket connection closed.');
        });

        this.websocket.on('error', (error) => {
            console.error('WebSocket error:', error);
        });
    }

    disconnectWebSocket() {
        if (this.websocket) {
            console.log('Disconnecting WebSocket...');
            this.websocket.close();
        }
    }
}