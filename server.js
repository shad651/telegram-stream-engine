require('dotenv').config();
const express = require('express');
const { TelegramClient } = require('telegram');
const { StringSession } = require('telegram/sessions');

const {
  TELEGRAM_API_ID,
  TELEGRAM_API_HASH,
  TELEGRAM_SESSION,
  TELEGRAM_CHANNEL_ID,
  BOT_TOKEN,
  RENDER_EXTERNAL_URL,
  PORT = 3000,
} = process.env;

if (!TELEGRAM_API_ID || !TELEGRAM_API_HASH || !TELEGRAM_SESSION || !TELEGRAM_CHANNEL_ID || !BOT_TOKEN) {
  console.error('❌ Missing required environment variables.');
  process.exit(1);
}

const app = express();
app.use(express.json());

let client = null;

async function getTelegramClient() {
  if (client && client.connected) return client;
  client = new TelegramClient(
    new StringSession(TELEGRAM_SESSION),
    parseInt(TELEGRAM_API_ID, 10),
    TELEGRAM_API_HASH,
    { connectionRetries: 5 }
  );
  await client.connect();
  console.log('✅ Telegram Client Connected');
  return client;
}

app.get('/', (req, res) => res.send('Server is active 🚀'));

// ---------- Fast Chunked Stream Endpoint ----------
app.get('/stream', async (req, res) => {
  try {
    const fileId = req.query.file_id;
    const msgId = req.query.msg_id;

    // Small File Stream (< 20 MB)
    if (fileId) {
      const getFileResp = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`);
      const fileData = await getFileResp.json();

      if (fileData.ok && fileData.result && fileData.result.file_path) {
        const downloadUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${fileData.result.file_path}`;
        const mediaResp = await fetch(downloadUrl, {
          headers: req.headers.range ? { 'Range': req.headers.range } : {}
        });

        res.setHeader('Content-Type', mediaResp.headers.get('content-type') || 'video/mp4');
        if (mediaResp.headers.get('content-length')) res.setHeader('Content-Length', mediaResp.headers.get('content-length'));
        if (mediaResp.headers.get('content-range')) {
          res.setHeader('Content-Range', mediaResp.headers.get('content-range'));
          res.status(206);
        }

        const arrayBuffer = await mediaResp.arrayBuffer();
        return res.send(Buffer.from(arrayBuffer));
      }
    }

    // Large File Stream (> 20 MB) with Fast Range Handling
    if (msgId) {
      const tgClient = await getTelegramClient();
      const messages = await tgClient.getMessages(TELEGRAM_CHANNEL_ID, { ids: [parseInt(msgId, 10)] });

      if (!messages || !messages[0] || !messages[0].media) {
        return res.status(404).send('Media not found on Channel');
      }

      const message = messages[0];
      const media = message.media.document || message.media.video || message.media.photo;
      const fileSize = media ? media.size : 0;

      const range = req.headers.range;
      let start = 0;
      let end = fileSize ? fileSize - 1 : 0;

      if (range && fileSize) {
        const parts = range.replace(/bytes=/, "").split("-");
        start = parseInt(parts[0], 10);
        end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;

        res.status(206);
        res.setHeader('Content-Range', `bytes ${start}-${end}/${fileSize}`);
        res.setHeader('Content-Length', (end - start) + 1);
      } else if (fileSize) {
        res.setHeader('Content-Length', fileSize);
      }

      res.setHeader('Content-Type', 'video/mp4');
      res.setHeader('Accept-Ranges', 'bytes');

      // Optimized for low RAM (128KB Chunks)
      const clientStream = tgClient.iterDownload({
        file: message.media,
        offset: BigInt(start),
        requestSize: 128 * 1024,
      });

      let bytesSent = 0;
      const bytesToFetch = end - start + 1;

      for await (const chunk of clientStream) {
        if (res.destroyed) break;
        res.write(chunk);
        bytesSent += chunk.length;
        if (bytesSent >= bytesToFetch) break;
      }

      return res.end();
    }

    res.status(400).send('Missing stream parameters.');
  } catch (error) {
    console.error('Streaming error:', error);
    if (!res.headersSent) res.status(500).send('Streaming Failed');
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
    const targetMsgId = msg.forward_from_message_id || msg.message_id;

    const baseUrl = RENDER_EXTERNAL_URL || 'https://telegram-stream-engine.onrender.com';
    
    let streamUrl = '';
    if (video && video.file_size && video.file_size < 20 * 1024 * 1024) {
      streamUrl = `${baseUrl}/stream?file_id=${video.file_id}`;
    } else {
      streamUrl = `${baseUrl}/stream?msg_id=${targetMsgId}`;
    }

    const replyText = `🎬 <b>Video Stream Link Ready!</b>\n\n` +
                      `🆔 <b>Msg ID:</b> <code>${targetMsgId}</code>\n\n` +
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
