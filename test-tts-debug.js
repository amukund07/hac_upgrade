const http = require('http');

const postData = JSON.stringify({
  text: 'This is a test narration. Please convert this to speech.',
  style: 'story'
});

console.log('Making TTS request to localhost:5000/api/tts');
console.log('Payload:', postData);

const options = {
  hostname: 'localhost',
  port: 5000,
  path: '/api/tts',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

const req = http.request(options, (res) => {
  console.log(`\n=== RESPONSE ===`);
  console.log(`STATUS: ${res.statusCode}`);
  console.log(`HEADERS:`, res.headers);
  
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('\n=== RESPONSE BODY ===');
    try {
      const parsed = JSON.parse(data);
      console.log('Success:', parsed.success);
      console.log('Message:', parsed.message);
      if (parsed.data) {
        console.log('Audio data length:', parsed.data.audioBase64?.length || 'N/A');
        console.log('Audio format:', parsed.data.format || 'N/A');
        console.log('Audio preview:', parsed.data.audioBase64?.substring(0, 80) || 'N/A');
      } else {
        console.log('Data:', parsed.data);
      }
    } catch (e) {
      console.log('Raw response:', data.substring(0, 500));
    }
  });
});

req.on('error', (e) => {
  console.error(`\n!!! REQUEST ERROR !!!`);
  console.error(`Error: ${e.message}`);
});

req.write(postData);
req.end();

console.log('\nWaiting for response...\n');
