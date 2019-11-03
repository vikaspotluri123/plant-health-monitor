module.exports = {
	init() {
		const {ipcRenderer} = require('electron');
		const setAction = require('./util/set-action');
		const setConnected = require('./util/set-connected');
		
		ipcRenderer.on('renderer-error', (_, error) => {
			window.alert(error);
		});
		
		ipcRenderer.on('backend-response', (_, [name, data]) => {
			console.log(`Backend Response (${name})`, data);
			switch (name) {
				case 'routingCompleted':
				setAction('Uploading Routes to drone');
				break;
				case 'routesUploaded':
				setAction('Waiting for drone to return');
				break;
				case 'navigationComplete':
				setAction('Waiting for SD card to be inserted');
				break;
				case 'mediaInserted':
				states[0].busy = false;
				setAction('Words go here');
				break;
				case 'drone.connected':
				setConnected(true);
				break;
				case 'drone.disconnected':
				setConnected(false);
				break;
				default:
				setAction(name);
			}
		});
		
		ipcRenderer.send('connection-status');
	}
}
