const LISTENERS = [
  'routingCompleted',
  'routesUploaded',
  'navigationComplete',
  'mediaInserted',
  'drone.disconnected',
  'drone.connected'
];

const {BrowserWindow, app, Tray, Menu, ipcMain} = require('electron');
const path = require('path');
const backend = require('./wrapper');

let win;

function addListener(eventName) {
  backend.events.addListener(eventName, data => {
    if (win) {
      win.webContents.send('backend-response', [eventName, data]);
    }
  });
}

ipcMain.on('backend-message', (_, [action, args]) => {
  switch(action) {
    case 'FLY':
      return backend.flyOver(...args);
    default:
      win.webContents.send('renderer-error', `Unknown action ${action} for backend`);
  }
});

// When the window requests the connection status, use official channels (backend-response)
// To update the connection status
ipcMain.on('connection-status', () => {
  if (win) {
    const code = backend.isConnected() ? 'drone.connected' : 'drone.disconnected';
    win.webContents.send('backend-response', [code]);
  }
});

LISTENERS.forEach(addListener);

function showWindow() {
  if (win) {
    win.focus();
    return;
  }

  // Create the browser window.
  win = new BrowserWindow({
    width: 1024,
    height: 800,
    webPreferences: {
      nodeIntegration: true
    }
  });

  win.center();
  win.removeMenu();
  win.loadFile('views/index.html');

  // Open the DevTools.
  win.webContents.openDevTools();

  // Emitted when the window is closed.
  win.on('closed', () => {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    win = null;
  });
};

const ICON_PATH = path.resolve(__dirname, 'resources/icon.png');
let tray;

function createContextMenu() {
  return Menu.buildFromTemplate([{
    label: 'Show',
    click: showWindow
  }, {
    label: 'Quit',
    click: () => app.quit()
  }]);
}

function createTray() {
  if (tray) {
    tray.destroy();
  }

  tray = new Tray(ICON_PATH);
  tray.setContextMenu(createContextMenu());
  tray.setToolTip('DPHM v0');
  tray.on('click', showWindow);
};


app.on('ready', () => {
  createTray();
  showWindow();
  console.log('Ready', {pid: process.pid});
});

// @todo - figure out what this actually does in Windows
app.on('activate', () => {
  console.log('activate called');
  showWindow();
});

// Prevent the app from closing when all of the windows close.
// The reason for doing this is the app is designed to be really lightweight
// by default. Since a majority of the time will be the app functioning as a
// Windows Service, there's no reason to keep the status window in memory
app.on('window-all-closed', () => {
  console.log('window-all-closed');
});
