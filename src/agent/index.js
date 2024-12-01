import { AgentWrapper } from './agent_wrapper.js';
import path from 'path';

const profileJackFp = path.join(path.resolve(), 'Jack.json');
const profileJaneFp = path.join(path.resolve(), 'Jane.json');
const profileJohnFp = path.join(path.resolve(), 'John.json');

const JackWebSocketUrl = `ws://localhost:8080/ws/Jack_client`;
const JaneWebSocketUrl = `ws://localhost:8080/ws/Jane_client`;
const JohnWebSocketUrl = `ws://localhost:8080/ws/John_client`;

(async () => {
    const JackAgent = new AgentWrapper(profileJackFp, JackWebSocketUrl);
    await JackAgent.initialize(true, 'Jack initialized', 1);

    const JaneAgent = new AgentWrapper(profileJaneFp, JaneWebSocketUrl);
    await JaneAgent.initialize(true, 'Jane initialized', 1);

    const JohnAgent = new AgentWrapper(profileJohnFp, JohnWebSocketUrl);
    await JohnAgent.initialize(true, 'John initialized', 1);

    process.on('SIGINT', () => {
        console.log('Gracefully shutting down...');
        JackAgent.disconnectWebSocket();
        JaneAgent.disconnectWebSocket();
        JohnAgent.disconnectWebSocket();
        process.exit(0);
    });
})();