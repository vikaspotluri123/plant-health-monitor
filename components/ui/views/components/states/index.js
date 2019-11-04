const StartState = require('./start');
const ProcessState = require('./process');
const ResultState = require('./results');

const start = new StartState();
const proces = new ProcessState();
const result = new ResultState();

start.next = proces;

proces.previous = start;
proces.next = result;

result.previous = proces;

module.exports = [
    start,
    proces,
    result
];