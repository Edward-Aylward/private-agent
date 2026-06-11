export function isMouseClicksDisabled(): boolean {
  return /^(1|true|yes|on)$/.test((process.env.Private_TUI_DISABLE_MOUSE_CLICKS ?? '').trim().toLowerCase())
}
