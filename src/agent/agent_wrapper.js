import { Agent } from './agent.js';
import WebSocket from 'ws';

export class AgentWrapper {
    constructor(profile_fp, websocketUrl) {
        this.agent = new Agent();
        this.websocketUrl = websocketUrl;
        this.websocket = null;
        this.profile_fp = profile_fp;
        this.serverResponse = null; // Cache server response
        this.pendingResponse = null; // Used for processing pending responses
    }

    async initialize(load_mem = false, init_message = null, count_id = 0) {
        console.log('Initializing agent wrapper...');
        await this.agent.start(this.profile_fp, load_mem, init_message, count_id);

        if (this.websocketUrl) {
            this.connectWebSocket();
        }

        // Hijack this.prompter.promptConvo
        const originalPromptConvo = this.agent.prompter.promptConvo.bind(this.agent.prompter);

        this.agent.prompter.promptConvo = async (history) => {
            console.log('Intercepting promptConvo call...');

            if (this.serverResponse) {
                // If there is already a cached server response, use it directly
                const response = this.serverResponse;
                this.serverResponse = null; // Clear the cache after using it
                console.log('Using cached server response:', response);
                return response;
            }

            console.log('Triggering pendingResponse with:', message.message);
            const serverResponse = await new Promise((resolve) => {
                this.pendingResponse = resolve; // Save the resolve function for triggering by the server message
                setTimeout(() => {
                    if (this.pendingResponse) {
                        console.log('Server response timed out. Falling back to default logic.');
                        resolve(null); // Return null after a timeout
                        this.pendingResponse = null; // Clear pendingResponse
                    }
                }, 10000); // Set a timeout duration (e.g., 10 seconds)
            });

            if (serverResponse) {
                console.log('Using server response:', serverResponse);
                return serverResponse;
            }

            console.log('No server response, falling back to original promptConvo...');
            return originalPromptConvo(history); // If no server response is available, call the original method
        };
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

                if (message.type === 'response') {
                    console.log('Server response received:', message.message);
                    this.serverResponse = message.message;

                    this.agent.bot.chat(`Server says: ${message.message}`); // Send a message in Minecraft

                    // If there is a pending Promise, trigger it immediately
                    if (this.pendingResponse) {
                        console.log('Triggering pendingResponse with:', message.message);
                        this.pendingResponse(message.message);
                        this.pendingResponse = null; // Clear pendingResponse to prevent duplicate triggers
                    }
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