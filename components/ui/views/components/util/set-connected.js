const el = require('../elements');

module.exports = isConnected => {
	window.isConnected = isConnected;
	const classAction = isConnected ? 'add' : 'remove';
	el.connection.textContent = isConnected ? 'Connected' : 'Disconnected';
	el.connection.parentElement.classList.remove('unknown');
	el.connection.parentElement.classList[classAction]('connected');
};