import { defineConfig,devices } from '@playwright/test';
const remote=process.env.PULSE_BASE_URL;
const baseURL=remote||'http://127.0.0.1:5173';
export default defineConfig({
  testDir:'./e2e',
  workers:2,
  use:{baseURL,channel:'msedge',launchOptions:{args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}},
  projects:[{name:'desktop',use:{...devices['Desktop Chrome'],viewport:{width:1440,height:1050}}},{name:'mobile',use:{...devices['iPhone 13'],defaultBrowserType:'chromium'}}],
  webServer:remote?undefined:{command:process.env.PULSE_PREVIEW?'npm run preview -- --port 5173':'npm run dev -- --port 5173',url:baseURL,reuseExistingServer:!process.env.PULSE_PREVIEW},
  reporter:'list',
});
