const axios = require('axios');
require('dotenv').config();

const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;

async function listModels() {
  try {
    console.log('Fetching available Gemini models...\n');
    const response = await axios.get(
      `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`
    );
    
    const models = response.data.models || [];
    const ttsModels = models.filter(m => m.name && m.name.includes('gemini'));
    
    console.log('Available Gemini Models:');
    console.log('='.repeat(80));
    
    ttsModels.forEach(model => {
      const name = model.name.replace('models/', '');
      const methods = model.supportedGenerationMethods || [];
      console.log(`\n${name}`);
      console.log(`  Supported methods: ${methods.join(', ')}`);
      if (model.description) {
        console.log(`  Description: ${model.description}`);
      }
    });
    
    console.log('\n' + '='.repeat(80));
    console.log(`\nTotal models found: ${ttsModels.length}`);
    
  } catch (error) {
    console.error('Error fetching models:', error.message);
    if (error.response?.data) {
      console.error('Response:', error.response.data);
    }
  }
}

listModels();
