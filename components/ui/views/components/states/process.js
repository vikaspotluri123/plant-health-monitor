const State = require('./start');

module.exports = class ProcessingState extends State {
    get parentNode() {
        return '#process';
    }
    
    set busy(value) {
        this.btn.disabled = value;
		this._busy = value;
	}
    
	init() {
        this.btn = this._parentNode.querySelector('.btn');
		this.on(this.btn, 'click', this.onSubmit.bind(this));
	}

	onSubmit(event) {
		event.preventDefault();

        this.busy = true;
        this.btn.innerHTML = 'Processing data...';
		console.log('do something')
	}
};