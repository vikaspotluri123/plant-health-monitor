const ACTION_MESSAGES = {
	'routingCompleted': 'Uploading Routes to drone',
	'routesUploaded': 'Waiting for drone to return',
	'copyingData': 'Copying images from SD card',
	'dataCopied': 'Stiching images into one big image',
	'imageProcessed': 'Successfully completed run',
};

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
			case 'navigationComplete':
				this.setAction('Waiting for SD card to be inserted');
				states[1].activate();
				break;
			case 'drone.connected':
				this.setConnected(true);
				break;
			case 'drone.disconnected':
				this.setConnected(false);
				break;
			case 'stichingCompleted':
				this.setAction('Determining at-risk regions');
				states[2].stitchedImage = data;
				states[2].activate();
				break;
			case 'imageProcessed': 
				this.setAction('Successfully completed run');
				states[2].highlightImage = data;
				states[2].activate();
				break;
			default:
				if (name in ACTION_MESSAGES) {
					this.setAction(ACTION_MESSAGES[name]);
				} else {
					this.setAction(name);
				}
		}
	}
}

module.exports = new IPCManager();
