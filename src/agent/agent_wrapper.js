import { Agent } from './agent.js';
import WebSocket from 'ws';
import fs from 'fs';
import { containsCommand, executeCommand, getCommand } from './commands/index.js';
import { stopRecording } from './viewer.js';

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

                if (message.type === 'agent_message') {
                    const parsedMessage = { data: { argument: message.message } };
                    let codeOutput = 'You did not take any action last time.';
                    if (parsedMessage.data && parsedMessage.data.argument) {
                        console.log('Agent action received:', parsedMessage.data.argument);
                        this.agent.bot.chat(`${parsedMessage.data.argument}`);

                        let modifiedArgument = parsedMessage.data.argument;
                        let command = containsCommand(modifiedArgument);
                        if (command) {
                            console.log(`Detected command: ${command}`);
                            let execute_res = await executeCommand(this.agent, modifiedArgument);
                            if (execute_res) {
                                execute_res = execute_res.replace(/[\r\n]+/g, ' ');
                                this.agent.bot.chat(execute_res);
                                codeOutput = execute_res;
                                console.log(codeOutput);
                            } else {
                                console.warn('Failed to execute command.');
                            }
                        }
                        if (this.pendingResponse) {
                            this.pendingResponse(parsedMessage.data.argument);
                            this.pendingResponse = null;
                        }
                    } else {
                        console.warn('Malformed agent_message format:', message.message);
                    }

                    try {
                        let stats = await getCommand('!stats').perform(this.agent);
                        let inventory = await getCommand('!inventory').perform(this.agent);                    

                        let visionResponse = '';
                        let latestImageUri = '';
                        if (fs.existsSync(`screenshots/${this.agent.name}/current_vision_response.txt`)) {
                            visionResponse = fs.readFileSync(`screenshots/${this.agent.name}/current_vision_response.txt`, 'utf8');
                            console.log('Vision Response:', visionResponse);
                        } else {
                            console.log('File current_vision_response.txt not found, skipping...');
                        }
                        if (fs.existsSync(`screenshots/${this.agent.name}/current_image_url.txt`)) {
                            latestImageUri = fs.readFileSync(`screenshots/${this.agent.name}/current_image_url.txt`, 'utf8');
                            console.log('Latest Image URI:', latestImageUri);
                        } else {
                            console.log('File current_image_url.txt not found, skipping...');
                        }

                        const serverPayload = {
                            type: 'agent_data',
                            stats: stats,
                            inventory: inventory,
                            visionResponse: visionResponse,
                            codeOutput: codeOutput,
                            latestImageUri: latestImageUri
                        };
                        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                            this.websocket.send(JSON.stringify(serverPayload));
                            console.log('Sent stats, inventory, visionResponse, codeOutput and latestImageUri to server:', serverPayload);
                        } else {
                            console.warn('WebSocket is not open. Failed to send serverPayload.');
                        }
                    } catch (error) {
                        console.error('Error fetching or sending serverPayload:', error);
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
            stopRecording(`temp_screenshots/${this.agent.name}`, `screenshots/${this.agent.name}`);
        });

        this.websocket.on('error', (error) => {
            console.error('WebSocket error:', error);
            stopRecording(`temp_screenshots/${this.agent.name}`, `screenshots/${this.agent.name}`);
        });
    }

    disconnectWebSocket() {
        if (this.websocket) {
            console.log('Disconnecting WebSocket...');
            this.websocket.close();
        }
    }
}