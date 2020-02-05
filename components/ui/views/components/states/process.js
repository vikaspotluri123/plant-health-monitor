const State = require('./start');
const ipc = require('../ipc');

module.exports = class ProcessingState extends State {
	get parentNode() {
		return '#process';
	}

	set busy(value) {
		this.btn.disabled = value;
		this.drive.disabled = value;
		this._busy = value;
	}

	reset() {
		this.busy = false;
	}

	init() {
		this.btn = this._parentNode.querySelector('.btn');
		this.drive = this._parentNode.querySelector('select');
		this.on(this.btn, 'click', this.onSubmit.bind(this));
	}

	onSubmit(event) {
		event.preventDefault();

		this.busy = true;
		this.btn.innerHTML = 'Processing data...';
		ipc.sendMessage(['process-data', this.drive.value]);
	}
};