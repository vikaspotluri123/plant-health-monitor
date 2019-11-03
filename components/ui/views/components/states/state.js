module.exports = class State {
    constructor() {
      this.events = [];
    }

    init() {
      // noop
    }

    on(node, event, fn) {
      this.events.push([node, event, fn]);
      node.addEventListener(event, fn);
    }

    destroy() {
      this.events.forEach(([thing, name, fn]) => thing.removeEventListener(name, fn));
    }
  }