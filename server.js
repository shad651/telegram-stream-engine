require('dotenv').config();
const express = require('express');

const {
  BOT_TOKEN,
  RENDER_EXTERNAL_URL,
  PORT = 3000,
} = process.env;

if (!BOT_TOKEN) {
  console.error('❌ Missing BOT_TOKEN variable.');
  process.exit(1);
}

const app = express();
app.use(express.json());

app.get('/', (req, res) => res.send('Server is active 🚀'));

// ---------- Direct Fast Bot File Stream Endpoint ----------
app.get('/stream', async (req, res) => {
  try {
    const fileId = req.query.file_id;
    if (!fileId) return res.status(400).send('Missing file_id parameter.');

    // Step 1: Get file path from Telegram Bot API
    const getFileResp = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`);
    const fileData = await getFileResp.json();

    if (!fileData.ok || !fileData.result.file_path) {
      return res.status(404).send('File not found on Telegram servers.');
    }

    const filePath = fileData.result.file_path;
    const downloadUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

    // Step 2: Stream file directly from Telegram File Server
    const mediaResp = await fetch(downloadUrl, {
      headers: req.headers.range ? { 'Range': req.headers.range } : {}
    });

    res.setHeader('Content-Type', mediaResp.headers.get('content-type') || 'video/mp4');
    if (mediaResp.headers.get('content-length')) {
      res.setHeader('Content-Length', mediaResp.headers.get('content-length'));
    }
    if (mediaResp.headers.get('content-range')) {
      res.setHeader('Content-Range', mediaResp.headers.get('content-range'));
      res.status(206);
    }

    const arrayBuffer = await mediaResp.arrayBuffer();
    res.send(Buffer.from(arrayBuffer));

  } catch (error) {
    console.error('Streaming Error:', error);
    if (!res.headersSent) res.status(500).send('Internal Server Error');
  }
});

// ---------- Telegram Bot Webhook Endpoint ----------
app.post('/bot-webhook', async (req, res) => {
  res.sendStatus(200);

  try {
    const update = req.body;
    const msg = update.message || update.channel_post || update.edited_message;
    if (!msg) return;

    const chatId = msg.chat.id;
    const video = msg.video || msg.document;

    if (!video || !video.file_id) {
      return;
    }

    const fileId = video.file_id;
    const baseUrl = RENDER_EXTERNAL_URL || 'https://telegram-stream-engine.onrender.com';
    const streamUrl = `${baseUrl}/stream?file_id=${fileId}`;

    const replyText = `🎬 <b>Video Stream Link Ready!</b>\n\n` +
                      `🔗 <b>Direct Stream Link:</b>\n${streamUrl}`;

    await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: replyText,
        parse_mode: 'HTML'
      })
    });
  } catch (err) {
    console.error("❌ Error in webhook:", err);
  }
});

app.listen(PORT, async () => {
  console.log(`🚀 Server running on port ${PORT}`);
  if (BOT_TOKEN && RENDER_EXTERNAL_URL) {
    try {
      await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${RENDER_EXTERNAL_URL}/bot-webhook`);
      console.log('🤖 Bot Webhook Configured');
    } catch (e) {
      console.error('Webhook error:', e);
    }
  }
});
