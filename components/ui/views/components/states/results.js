const State = require('./start');
const ipc = require('../ipc');

module.exports = class ResultState extends State {
    get parentNode() {
        return '#results';
    }

    init() {
        this.initialized = true;
        this._stitchedNode = this._parentNode.querySelector('#stitched');
        this._highlightNode = this._parentNode.querySelector('#marked');
        this._wrapper = this._parentNode.querySelector('#top-image');
        this._slider = this._parentNode.querySelector('#comparison-selector');
        this._slider.oninput = () => this._wrapper.style.width = `${this._slider.value}%`;

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

    reset() {
        this._highlightImage = null;
        this._stitchedImage = null;
        this.rerender();
    }
};