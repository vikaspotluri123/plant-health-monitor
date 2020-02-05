module.exports = class State {
  get parentNode() {
    throw new Error('Parent Node must be provided');
  }

  constructor() {
    this.events = [];
    this._previous = null;
    this._next = null;
    this._parentNode = document.querySelector(this.parentNode);
  }

  set previous(state) {
    if (!state instanceof State) {
      throw new Error('PreviousState must extend the State class');
    }

    this._previous = state;
  }

  set next(state) {
    if (!state instanceof State) {
      throw new Error('NextState must extend the State class');
    }

    this._next = state;
  }

  activate() {
    this._parentNode.style.display = 'flex';
    this.init();
    this._previous && this._previous.deactivate(false, true);
    this._next && this._next.deactivate(true, false);
  }

  deactivate(handleNext = false, handlePrev = false) {
    this._parentNode.style.display = 'none';

    if (handlePrev) {
      this._previous && this._previous.deactivate(false, true);
    }

    if (handleNext) {
      this._next && this._next.deactivate(true, false);
    }
  }

  init() {
    // noop
  }

  reset() {
    console.warn(this.constructor.name, 'has not implemented reset');
  }

  on(node, event, fn) {
    this.events.push([node, event, fn]);
    node.addEventListener(event, fn);
  }

  destroy() {
    this.events.forEach(([thing, name, fn]) => thing.removeEventListener(name, fn));
  }
}