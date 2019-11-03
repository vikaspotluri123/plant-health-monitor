const State = require('./state');

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

	init() {
		this.btn = document.querySelector('#start .btn');
		this.on(this.btn, 'click', this.onSubmit.bind(this));
	}

	onSubmit(event) {
		event.preventDefault();

		if (!window.isConnected) {
			window.alert('Not connected to drone');
			setConnected(true);
			return;
		}

		this.busy = true;
		console.log('Sending message');
		setAction('Computing best route');
		ipcRenderer.send('backend-message', ['FLY', 'a']);
	}
}