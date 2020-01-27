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
		this.launchBtn.disabled = value;
		this._busy = value;
	}

	deactivate(...args) {
		super.deactivate(...args);
		this._busy = false;
	}

	init() {
		this.plotBtn = document.querySelector('#start .plot');
		this.launchBtn = document.querySelector('#start .launch');
		this.on(this.launchBtn, 'click', this.onSubmit.bind(this));
		this.on(this.plotBtn, 'click', this.requestPlot.bind(this));
	}

	async getPoints() {
		const points = await this._map.executeJavaScript('points');

		if (!points || points.length !== 4) {
			try {
				await this._map.executeJavaScript('switchToDraw()');
			} finally {
				await dialog.showMessageBox(null, {message: 'Please select a valid region in the map', title: 'Invalid Region - DPHM v0', type: 'error'});
			}

			return;
		}

		return points;
	}

	async requestPlot(event) {
		event.preventDefault();
		this.plotBtn.disabled = true;

		const points = await this.getPoints();

		if (!Array.isArray(points)) {
			this.plotBtn.disabled = false;
			return;
		}

		ipc.sendMessage(['plot', points]);
	}

	async handleBadPlot() {
		await dialog.showMessageBox(null, {message: 'something broke 🙃', title: 'Something broke!'});
		this.plotBtn.disabled = false;
	}

	async plot(data) {
		const dta = JSON.stringify(data);
		await this._map.executeJavaScript(`renderPoints(${dta})`);
		this.plotBtn.disabled = false;
	}

	async onSubmit(event) {
		event.preventDefault();

		const points = await this.getPoints();

		if (!points) {
			return;
		}

		if (!window.isConnected) {
			await dialog.showMessageBox(null, {message: 'Not connected to drone', title: 'Connection Error - DPHM v0', type: 'error'});
			ipc.setConnected(true);
			return;
		}

		this.busy = true;
		console.log('Sending message');
		ipc.setAction('Computing best route');
		ipc.sendMessage(['FLY', points]);
	}
}