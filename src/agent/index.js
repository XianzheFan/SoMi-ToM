import { AgentWrapper } from './agent_wrapper.js';
import path from 'path';

const profile_fp = path.join(path.resolve(), 'andy.json');
const websocketUrl = 'ws://localhost:8080';

(async () => {
    const agentWrapper = new AgentWrapper(profile_fp, websocketUrl);
    await agentWrapper.initialize(true, 'Agent initialized', 1);

    process.on('SIGINT', () => {
        console.log('Gracefully shutting down...');
        agentWrapper.disconnectWebSocket();
        process.exit(0);
    });
})();