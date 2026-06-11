import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { canOpenSessionWindow, openSessionInNewWindow } from './windows'

const desktopWindow = window as unknown as { PrivateDesktop?: Window['PrivateDesktop'] }
const initialPrivateDesktop = desktopWindow.PrivateDesktop

const notifyError = vi.fn()

vi.mock('./notifications', () => ({
  notifyError: (...args: unknown[]) => notifyError(...args)
}))

function installBridge(openSessionWindow?: Window['PrivateDesktop']['openSessionWindow']) {
  desktopWindow.PrivateDesktop = {
    ...(openSessionWindow ? { openSessionWindow } : {})
  } as unknown as Window['PrivateDesktop']
}

beforeEach(() => {
  notifyError.mockClear()
})

afterEach(() => {
  if (initialPrivateDesktop) {
    desktopWindow.PrivateDesktop = initialPrivateDesktop
  } else {
    delete desktopWindow.PrivateDesktop
  }
})

describe('canOpenSessionWindow', () => {
  it('is false when the desktop bridge is absent', () => {
    delete desktopWindow.PrivateDesktop
    expect(canOpenSessionWindow()).toBe(false)
  })

  it('is false when the bridge lacks openSessionWindow', () => {
    installBridge(undefined)
    expect(canOpenSessionWindow()).toBe(false)
  })

  it('is true when the bridge exposes openSessionWindow', () => {
    installBridge(vi.fn().mockResolvedValue({ ok: true }))
    expect(canOpenSessionWindow()).toBe(true)
  })
})

describe('openSessionInNewWindow', () => {
  it('no-ops without a session id', async () => {
    const open = vi.fn().mockResolvedValue({ ok: true })
    installBridge(open)

    await openSessionInNewWindow('')

    expect(open).not.toHaveBeenCalled()
    expect(notifyError).not.toHaveBeenCalled()
  })

  it('no-ops gracefully when the bridge is absent (web fallback)', async () => {
    delete desktopWindow.PrivateDesktop

    await openSessionInNewWindow('s1')

    expect(notifyError).not.toHaveBeenCalled()
  })

  it('invokes the bridge with the session id', async () => {
    const open = vi.fn().mockResolvedValue({ ok: true })
    installBridge(open)

    await openSessionInNewWindow('s1')

    expect(open).toHaveBeenCalledWith('s1')
    expect(notifyError).not.toHaveBeenCalled()
  })

  it('notifies on an ok:false result', async () => {
    installBridge(vi.fn().mockResolvedValue({ ok: false, error: 'invalid-session-id' }))

    await openSessionInNewWindow('s1')

    expect(notifyError).toHaveBeenCalledTimes(1)
  })

  it('notifies when the bridge throws', async () => {
    installBridge(vi.fn().mockRejectedValue(new Error('boom')))

    await openSessionInNewWindow('s1')

    expect(notifyError).toHaveBeenCalledTimes(1)
  })
})
