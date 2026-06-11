const { contextBridge, ipcRenderer, webUtils } = require('electron')

contextBridge.exposeInMainWorld('PrivateDesktop', {
  getConnection: profile => ipcRenderer.invoke('Private:connection', profile),
  revalidateConnection: () => ipcRenderer.invoke('Private:connection:revalidate'),
  touchBackend: profile => ipcRenderer.invoke('Private:backend:touch', profile),
  getGatewayWsUrl: profile => ipcRenderer.invoke('Private:gateway:ws-url', profile),
  openSessionWindow: sessionId => ipcRenderer.invoke('Private:window:openSession', sessionId),
  getBootProgress: () => ipcRenderer.invoke('Private:boot-progress:get'),
  getConnectionConfig: profile => ipcRenderer.invoke('Private:connection-config:get', profile),
  saveConnectionConfig: payload => ipcRenderer.invoke('Private:connection-config:save', payload),
  applyConnectionConfig: payload => ipcRenderer.invoke('Private:connection-config:apply', payload),
  testConnectionConfig: payload => ipcRenderer.invoke('Private:connection-config:test', payload),
  probeConnectionConfig: remoteUrl => ipcRenderer.invoke('Private:connection-config:probe', remoteUrl),
  oauthLoginConnectionConfig: remoteUrl => ipcRenderer.invoke('Private:connection-config:oauth-login', remoteUrl),
  oauthLogoutConnectionConfig: remoteUrl => ipcRenderer.invoke('Private:connection-config:oauth-logout', remoteUrl),
  profile: {
    get: () => ipcRenderer.invoke('Private:profile:get'),
    set: name => ipcRenderer.invoke('Private:profile:set', name)
  },
  api: request => ipcRenderer.invoke('Private:api', request),
  notify: payload => ipcRenderer.invoke('Private:notify', payload),
  requestMicrophoneAccess: () => ipcRenderer.invoke('Private:requestMicrophoneAccess'),
  readFileDataUrl: filePath => ipcRenderer.invoke('Private:readFileDataUrl', filePath),
  readFileText: filePath => ipcRenderer.invoke('Private:readFileText', filePath),
  selectPaths: options => ipcRenderer.invoke('Private:selectPaths', options),
  writeClipboard: text => ipcRenderer.invoke('Private:writeClipboard', text),
  saveImageFromUrl: url => ipcRenderer.invoke('Private:saveImageFromUrl', url),
  saveImageBuffer: (data, ext) => ipcRenderer.invoke('Private:saveImageBuffer', { data, ext }),
  saveClipboardImage: () => ipcRenderer.invoke('Private:saveClipboardImage'),
  getPathForFile: file => {
    try {
      return webUtils.getPathForFile(file) || ''
    } catch {
      return ''
    }
  },
  normalizePreviewTarget: (target, baseDir) => ipcRenderer.invoke('Private:normalizePreviewTarget', target, baseDir),
  watchPreviewFile: url => ipcRenderer.invoke('Private:watchPreviewFile', url),
  stopPreviewFileWatch: id => ipcRenderer.invoke('Private:stopPreviewFileWatch', id),
  setTitleBarTheme: payload => ipcRenderer.send('Private:titlebar-theme', payload),
  setPreviewShortcutActive: active => ipcRenderer.send('Private:previewShortcutActive', Boolean(active)),
  openExternal: url => ipcRenderer.invoke('Private:openExternal', url),
  fetchLinkTitle: url => ipcRenderer.invoke('Private:fetchLinkTitle', url),
  sanitizeWorkspaceCwd: cwd => ipcRenderer.invoke('Private:workspace:sanitize', cwd),
  settings: {
    getDefaultProjectDir: () => ipcRenderer.invoke('Private:setting:defaultProjectDir:get'),
    setDefaultProjectDir: dir => ipcRenderer.invoke('Private:setting:defaultProjectDir:set', dir),
    pickDefaultProjectDir: () => ipcRenderer.invoke('Private:setting:defaultProjectDir:pick')
  },
  revealLogs: () => ipcRenderer.invoke('Private:logs:reveal'),
  getRecentLogs: () => ipcRenderer.invoke('Private:logs:recent'),
  readDir: dirPath => ipcRenderer.invoke('Private:fs:readDir', dirPath),
  gitRoot: startPath => ipcRenderer.invoke('Private:fs:gitRoot', startPath),
  terminal: {
    dispose: id => ipcRenderer.invoke('Private:terminal:dispose', id),
    resize: (id, size) => ipcRenderer.invoke('Private:terminal:resize', id, size),
    start: options => ipcRenderer.invoke('Private:terminal:start', options),
    write: (id, data) => ipcRenderer.invoke('Private:terminal:write', id, data),
    onData: (id, callback) => {
      const channel = `Private:terminal:${id}:data`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)
      return () => ipcRenderer.removeListener(channel, listener)
    },
    onExit: (id, callback) => {
      const channel = `Private:terminal:${id}:exit`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)
      return () => ipcRenderer.removeListener(channel, listener)
    }
  },
  onClosePreviewRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('Private:close-preview-requested', listener)
    return () => ipcRenderer.removeListener('Private:close-preview-requested', listener)
  },
  onOpenUpdatesRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('Private:open-updates', listener)
    return () => ipcRenderer.removeListener('Private:open-updates', listener)
  },
  onDeepLink: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('Private:deep-link', listener)
    return () => ipcRenderer.removeListener('Private:deep-link', listener)
  },
  signalDeepLinkReady: () => ipcRenderer.invoke('Private:deep-link-ready'),
  onWindowStateChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('Private:window-state-changed', listener)
    return () => ipcRenderer.removeListener('Private:window-state-changed', listener)
  },
  onPreviewFileChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('Private:preview-file-changed', listener)
    return () => ipcRenderer.removeListener('Private:preview-file-changed', listener)
  },
  onBackendExit: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('Private:backend-exit', listener)
    return () => ipcRenderer.removeListener('Private:backend-exit', listener)
  },
  onPowerResume: callback => {
    const listener = () => callback()
    ipcRenderer.on('Private:power-resume', listener)
    return () => ipcRenderer.removeListener('Private:power-resume', listener)
  },
  onBootProgress: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('Private:boot-progress', listener)
    return () => ipcRenderer.removeListener('Private:boot-progress', listener)
  },
  // First-launch bootstrap progress -- emitted by the install.ps1 stage
  // runner in main.cjs (apps/desktop/electron/bootstrap-runner.cjs).
  // Renderer's install overlay subscribes to live events and queries the
  // current snapshot via getBootstrapState() to recover after a devtools
  // reload mid-bootstrap.
  getBootstrapState: () => ipcRenderer.invoke('Private:bootstrap:get'),
  resetBootstrap: () => ipcRenderer.invoke('Private:bootstrap:reset'),
  repairBootstrap: () => ipcRenderer.invoke('Private:bootstrap:repair'),
  cancelBootstrap: () => ipcRenderer.invoke('Private:bootstrap:cancel'),
  onBootstrapEvent: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('Private:bootstrap:event', listener)
    return () => ipcRenderer.removeListener('Private:bootstrap:event', listener)
  },
  getVersion: () => ipcRenderer.invoke('Private:version'),
  uninstall: {
    summary: () => ipcRenderer.invoke('Private:uninstall:summary'),
    run: mode => ipcRenderer.invoke('Private:uninstall:run', { mode })
  },
  updates: {
    check: () => ipcRenderer.invoke('Private:updates:check'),
    apply: opts => ipcRenderer.invoke('Private:updates:apply', opts),
    getBranch: () => ipcRenderer.invoke('Private:updates:branch:get'),
    setBranch: name => ipcRenderer.invoke('Private:updates:branch:set', name),
    onProgress: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('Private:updates:progress', listener)
      return () => ipcRenderer.removeListener('Private:updates:progress', listener)
    }
  },
  themes: {
    fetchMarketplace: id => ipcRenderer.invoke('Private:vscode-theme:fetch', id),
    searchMarketplace: query => ipcRenderer.invoke('Private:vscode-theme:search', query)
  }
})
