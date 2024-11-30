import { AgentWrapper } from './agent_wrapper.js';
import path from 'path';

const profile_fp = path.join(path.resolve(), 'andy.json');
const clientId = 'andy_client';
const websocketUrl = `ws://localhost:8080/ws/${clientId}`;

(async () => {
    const agentWrapper = new AgentWrapper(profile_fp, websocketUrl);
    await agentWrapper.initialize(true, 'Agent initialized', 1);
    process.on('SIGINT', () => {
        console.log('Gracefully shutting down...');
        agentWrapper.disconnectWebSocket();
        process.exit(0);
    });
})();

// import { AgentWrapper } from './agent_wrapper.js';
// import path from 'path';

// const profile_fp1 = path.join(path.resolve(), 'andy.json');
// const profile_fp2 = path.join(path.resolve(), 'randy.json');
// const websocketUrl1 = 'ws://localhost:8081';
// const websocketUrl2 = 'ws://localhost:8082';

// (async () => {
//     const agentWrapper1 = new AgentWrapper(profile_fp1, websocketUrl1);
//     const agentWrapper2 = new AgentWrapper(profile_fp2, websocketUrl2);

//     await agentWrapper1.initialize(true, 'Agent 1 initialized', 1);
//     await agentWrapper2.initialize(true, 'Agent 2 initialized', 2);

//     process.on('SIGINT', () => {
//         console.log('Gracefully shutting down...');
//         agentWrapper1.disconnectWebSocket();
//         agentWrapper2.disconnectWebSocket();
//         process.exit(0);
//     });
// })();