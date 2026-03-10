const WebSocket = require('ws');
const http = require('http');

const PORT = process.env.PORT || 8080;

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Device Status Dashboard Server');
});

const wss = new WebSocket.Server({ server });

// Store the latest state of devices
// structure:
// {
//   'macos': { battery: 100, memoryUsedPercent: 45, cpuPercent: 12, foregroundApp: 'Safari', timestamp: 123456 },
//   'android': { battery: 80, foregroundApp: 'YouTube', timestamp: 123456 }
// }
const deviceStates = {};

function broadcastState() {
  const stateStr = JSON.stringify({ type: 'state_update', states: deviceStates });
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(stateStr);
    }
  });
}

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Send current state immediately upon connection
  ws.send(JSON.stringify({ type: 'state_update', states: deviceStates }));

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      if (data.type === 'device_update') {
        const { deviceId, state } = data;
        
        if (deviceId && state) {
          deviceStates[deviceId] = {
            ...state,
            timestamp: Date.now()
          };
          console.log(`Updated state for ${deviceId}:`, state);
          broadcastState();
        }
      }
    } catch (err) {
      console.error('Failed to parse message:', err);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

server.listen(PORT, () => {
  console.log(`Backend server listening on port ${PORT}`);
});
