import 'dotenv/config'
import { connectDatabase, disconnectDatabase } from '../src/config/db'
import { seedDatabase } from '../src/services/seedService'

const seed = async () => {
  await connectDatabase()
  await seedDatabase()

  await disconnectDatabase()
  console.log('Seeding complete')
}

seed().catch((err) => {
  console.error('Seeding error', err)
  process.exit(1)
})
