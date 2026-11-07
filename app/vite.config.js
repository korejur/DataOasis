import { defineConfig } from 'vite';

// base: './' da build radi i u podmapi (npr. GitHub Pages: /<repo>/).
export default defineConfig({
  base: './',
  build: {
    target: 'es2022',
    chunkSizeWarningLimit: 1500,
  },
});
