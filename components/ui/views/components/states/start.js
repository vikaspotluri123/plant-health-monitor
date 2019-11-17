const {dialog} = require('electron').remote;
const State = require('./state');
const ipc = require('../ipc');

module.exports = class StartState extends State {
	get parentNode() {
		return '#start';
	}

	constructor() {
		super();
		this._busy = false;
		this._map = document.getElementById('map');
	}

	set busy(value) {
		this.btn.disabled = value;
		this._busy = value;
	}

	deactivate(...args) {
		super.deactivate(...args);
		this._busy = false;
	}

	init() {
		this.btn = document.querySelector('#start .btn');
		this.on(this.btn, 'click', this.onSubmit.bind(this));
	}

	async onSubmit(event) {
		event.preventDefault();

		const points = await this._map.executeJavaScript('points');

		if (!points || points.length !== 4) {
			try {
				await this._map.executeJavaScript('switchToDraw()');
			} finally {
				await dialog.showMessageBox(null, {message: 'Please select a valid region in the map', title: 'Invalid Region - DPHM 1.0', type: 'error'});
			}

			return;
		}

		if (!window.isConnected) {
			await dialog.showMessageBox(null, {message: 'Not connected to drone', title: 'Connection Error - DPHM 1.0', type: 'error'});
			ipc.setConnected(true);
			return;
		}

		this.busy = true;
		console.log('Sending message');
		ipc.setAction('Computing best route');
		ipc.sendMessage(['FLY', points]);
	}
}