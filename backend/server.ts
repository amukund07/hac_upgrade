import { app } from './src/app'
import { connectDatabase } from './src/config/db'
import { env } from './src/config/env'

const startServer = async () => {
  await connectDatabase()

  app.listen(env.port, () => {
    // eslint-disable-next-line no-console
    console.log(`Hackostic API listening on port ${env.port}`)
  })
}

void startServer()