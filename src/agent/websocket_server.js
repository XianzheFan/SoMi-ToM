import WebSocket, { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 8080 });
wss.on('connection', (ws) => {
    console.log('Client connected.');
    ws.on('message', (message) => {
        console.log('Received from client:', message);
        ws.send(JSON.stringify({ type: 'response', message: 'Message received' }));
    });
    ws.on('close', () => {
        console.log('Client disconnected.');
    });
    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

console.log('WebSocket server is running on ws://localhost:8080');