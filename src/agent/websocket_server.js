import { WebSocketServer } from 'ws';
const wss = new WebSocketServer({ port: 8080 }, () => {
    console.log('WebSocket server started on ws://localhost:8080');
});

// Processing connection
wss.on('connection', (ws) => {
    console.log('New client connected.');
    ws.send(JSON.stringify({ type: 'status', message: 'Welcome to the WebSocket server!' }));

    // Receiving messages from the client
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log('Received message from client:', data);

            // Responding based on the message type
            if (data.type === 'status') {
                console.log('Agent status:', data.message);
            } else if (data.type === 'command') {
                console.log('Command received:', data.command);
                // Sending a response to the client
                ws.send(JSON.stringify({
                    type: 'response',
                    message: `Server response to command: ${data.command}`
                }));
            } else {
                console.warn('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    });

    ws.on('close', () => {
        console.log('Client disconnected.');
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });

    // Simulating periodic response messages
    setInterval(() => {
        ws.send(JSON.stringify({
            type: 'response',
            message: 'Periodic server message'
        }));
    }, 10000); // Sending once every 10 seconds
});