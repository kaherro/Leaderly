import { spawn } from 'node:child_process'

export function leaderlyServerPlugin(options = {}) {
  const {
    command = 'python',
    args = ['src/api/ws-api.py'],
    cwd = process.cwd(),
    enabled = true,
    env = {}
  } = options

  let child = null

  return {
    name: 'leaderly-server-plugin',
    apply: 'serve',
    configureServer(server) {
      if (!enabled || child) {
        return
      }

      child = spawn(command, args, {
        cwd,
        env: {
          ...process.env,
          ...env
        },
        stdio: 'inherit',
        shell: true
      })

      const stopChild = () => {
        if (!child || child.killed) {
          return
        }

        child.kill()
      }

      server.httpServer?.once('close', stopChild)
      process.once('exit', stopChild)
      process.once('SIGINT', stopChild)
      process.once('SIGTERM', stopChild)
    }
  }
}
