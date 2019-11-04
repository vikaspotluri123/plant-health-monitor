const State = require('./start');
const ipc = require('../ipc');

module.exports = class ProcessingState extends State {
    get parentNode() {
        return '#results';
    }

    init() {
        this.initialized = true;
        this._stitchedNode = this._parentNode.querySelector('#stitched');
        this._highlightNode = this._parentNode.querySelector('#marked');
        this.rerender();
    }

    set stitchedImage(image) {
        this._stitchedImage = image;
        this.rerender();
    }
    
    set highlightImage(image) {
        this._highlightImage = image;
        this.rerender();
    }
    
    rerender() {
        if (!this.initialized) {
            return;
        }

        if (this._stitchedImage) {
            this._stitchedNode.setAttribute('src', this._stitchedImage);
        }
        
        if (this._highlightImage) {
            this._highlightNode.setAttribute('src', this._highlightImage);
        }
    }

	onSubmit(event) {
		event.preventDefault();

        this.busy = true;
		this.btn.innerHTML = 'Processing data...';
		ipc.sendMessage(['process-data', this.drive.value]);
	}
};