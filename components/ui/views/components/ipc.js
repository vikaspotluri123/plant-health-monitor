class IPCManager {
	constructor() {
		this._ipc = null;
	}

	init() {
		const {ipcRenderer} = require('electron');

		this.initialized = true;
		this.setAction = require('./util/set-action');
		this.setConnected = require('./util/set-connected');
		this.ipc = ipcRenderer;
		
		ipcRenderer.on('backend-response', (...args) =>  this._processResponse(...args));
		ipcRenderer.on('renderer-error', (_, error) => {
			window.alert(error);
		});
		ipcRenderer.send('connection-status');
	}

	sendMessage(payload) {
		if (!this.initialized) {
			throw new Error('Not initialized');
		}

		this.ipc.send('backend-message', payload);
	}

	_processResponse(_, [name, data]) {
		console.log(`Backend Response (${name})`, data);
		switch (name) {
			case 'routingCompleted':
				this.setAction('Uploading Routes to drone');
				break;
			case 'routesUploaded':
				this.setAction('Waiting for drone to return');
				break;
			case 'navigationComplete':
				this.setAction('Waiting for SD card to be inserted');
				break;
			case 'mediaInserted':
				states[0].busy = false;
				this.setAction('Words go here');
				break;
			case 'drone.connected':
				this.setConnected(true);
				break;
			case 'drone.disconnected':
				this.setConnected(false);
				break;
			default:
				this.setAction(name);
		}
	}
}

module.exports = new IPCManager();
