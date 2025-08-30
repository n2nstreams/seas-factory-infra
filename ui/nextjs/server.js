const { createServer } = require('http')
const { parse } = require('url')
const next = require('next')

const dev = process.env.NODE_ENV !== 'production'
const hostname = process.env.HOSTNAME || 'localhost'
const port = process.env.PORT || 3000

// Prepare the Next.js app
const app = next({ dev, hostname, port })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  // Create HTTP server
  const server = createServer(async (req, res) => {
    try {
      // Parse the URL
      const parsedUrl = parse(req.url, true)
      
      // Handle WebSocket upgrade requests
      if (req.headers.upgrade && req.headers.upgrade.toLowerCase() === 'websocket') {
        // WebSocket upgrade will be handled by the WebSocket server
        // For now, just pass through to Next.js
        await handle(req, res, parsedUrl)
        return
      }
      
      // Handle regular HTTP requests
      await handle(req, res, parsedUrl)
    } catch (err) {
      console.error('Error occurred handling request:', err)
      res.statusCode = 500
      res.end('Internal Server Error')
    }
  })

  // Initialize WebSocket server
  try {
    const { initializeWebSocketServer } = require('./src/lib/websocket-server')
    initializeWebSocketServer(server)
    console.log('✅ WebSocket server initialized successfully')
  } catch (error) {
    console.warn('⚠️ WebSocket server initialization failed:', error.message)
    console.log('Continuing without WebSocket support...')
  }

  // Start the server
  server.listen(port, (err) => {
    if (err) throw err
    console.log(`> Ready on http://${hostname}:${port}`)
    console.log(`> WebSocket server available on ws://${hostname}:${port}`)
  })

  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully...')
    
    try {
      const { shutdownWebSocketServer } = require('./src/lib/websocket-server')
      shutdownWebSocketServer()
    } catch (error) {
      console.warn('Failed to shutdown WebSocket server:', error.message)
    }
    
    server.close(() => {
      console.log('HTTP server closed')
      process.exit(0)
    })
  })

  process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully...')
    
    try {
      const { shutdownWebSocketServer } = require('./src/lib/websocket-server')
      shutdownWebSocketServer()
    } catch (error) {
      console.warn('Failed to shutdown WebSocket server:', error.message)
    }
    
    server.close(() => {
      console.log('HTTP server closed')
      process.exit(0)
    })
  })
})
