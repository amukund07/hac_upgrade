import axios from 'axios'
import dotenv from 'dotenv'

dotenv.config()

const apiKey = process.env.GEMINI_API_KEY

async function main() {
  try {
    const response = await axios.get(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`)
    console.log(JSON.stringify(response.data, null, 2))
  } catch (err) {
    if (axios.isAxiosError(err)) {
      console.error(err.response?.data || err.message)
    } else {
      console.error(err)
    }
  }
}

main()
