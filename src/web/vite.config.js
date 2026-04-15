import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  if (mode === 'lib') {
    return {
      plugins: [vue()],
      build: {
        lib: {
          entry: 'lib/index.js',
          name: 'LeaderlyUI',
          fileName: (format) => `leaderly-ui.${format}.js`,
          formats: ['es', 'umd']
        },
        rollupOptions: {
          external: ['vue'],
          output: {
            exports: 'named',
            globals: {
              vue: 'Vue'
            }
          }
        }
      }
    }
  }

  return {
    plugins: [vue()],
    server: {
      port: 5173
    }
  }
})
