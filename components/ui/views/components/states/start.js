const State = require('./state');
const ipc = require('../ipc');

module.exports = class StartState extends State {
	get parentNode() {
		return '#start';
	}
	
	constructor() {
		super();
		this._busy = false;
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

	onSubmit(event) {
		event.preventDefault();

		if (!window.isConnected) {
			window.alert('Not connected to drone');
			ipc.setConnected(true);
			return;
		}

		this.busy = true;
		console.log('Sending message');
		ipc.setAction('Computing best route');
		ipc.sendMessage(['FLY', 'a']);
	}
}