// Configuration dari environment variables
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  wsBaseUrl: import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000',
  appName: import.meta.env.VITE_APP_NAME || 'ABIS Interview Assistant',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  env: import.meta.env.VITE_ENV || 'development',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
}

export default config
