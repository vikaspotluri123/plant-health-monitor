const StartState = require('./start');
const ProcessState = require('./process');

const start = new StartState();
const proces = new ProcessState();

start.next = proces;
proces.previous = start;

module.exports = [
    start,
    proces
];