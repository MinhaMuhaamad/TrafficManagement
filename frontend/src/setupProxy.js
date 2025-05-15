const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use('/socket.io', createProxyMiddleware({
    target: 'http://localhost:8000',
    ws: true,
    changeOrigin: true,
    logLevel: 'debug',
    onError: (err) => {
      console.log('Proxy Error:', err);
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  }));
};
