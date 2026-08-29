require('dotenv').config();
const express = require('express');
const { TelegramClient } = require('telegram');
const { StringSession } = require('telegram/sessions');
const { Readable } = require('stream');

const {
  TELEGRAM_API_ID,
  TELEGRAM_API_HASH,
  TELEGRAM_SESSION,
  TELEGRAM_CHANNEL_ID,
  BOT_TOKEN,
  RENDER_EXTERNAL_URL,
  PORT = 3000,
} = process.env;

if (!TELEGRAM_API_ID || !TELEGRAM_API_HASH || !TELEGRAM_SESSION || !TELEGRAM_CHANNEL_ID) {
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

// Health Check Endpoint (Keep-Alive)
app.get('/', (req, res) => {
  res.send('Server is active and running 🚀');
});

// ---------- Direct Stream Endpoint ----------
app.get('/stream', async (req, res) => {
  try {
    const msgId = parseInt(req.query.msg_id, 10);
    if (!msgId) return res.status(400).send('Missing msg_id parameter.');

    const tgClient = await getTelegramClient();
    const messages = await tgClient.getMessages(TELEGRAM_CHANNEL_ID, { ids: [msgId] });

    if (!messages || !messages[0] || !messages[0].media) {
      return res.status(404).send('Video or message not found.');
    }

    const message = messages[0];
    const media = message.media.document || message.media.photo;
    const fileSize = media ? media.size : 0;

    const range = req.headers.range;
    res.setHeader('Content-Type', 'video/mp4');
    res.setHeader('Accept-Ranges', 'bytes');

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

    const stream = new Readable({ read() {} });
    
    res.on('close', () => {
      stream.destroy();
    });

    tgClient.downloadMedia(message.media, {
      offset: BigInt(start),
      limit: end - start + 1,
      workers: 1,
      output: stream
    }).catch(err => {
      console.error('Download stream error:', err);
      if (!res.headersSent) res.status(500).send('Streaming error');
    });

    stream.pipe(res);
  } catch (error) {
    console.error('Error in /stream:', error);
    if (!res.headersSent) res.status(500).send('Internal Server Error');
  }
});

// ---------- Telegram Bot Webhook Endpoint ----------
app.post('/bot-webhook', async (req, res) => {
  res.sendStatus(200);

  try {
    const update = req.body;
    console.log("📩 Webhook Event Received:", JSON.stringify(update));

    const msg = update.message || update.channel_post || update.edited_message;
    if (!msg) return;

    const chatId = msg.chat.id;
    const targetMsgId = msg.forward_from_message_id || msg.message_id;

    const baseUrl = RENDER_EXTERNAL_URL || 'https://telegram-stream-engine.onrender.com';
    const streamUrl = `${baseUrl}/stream?msg_id=${targetMsgId}`;

    const replyText = `🎬 <b>Video Stream Link Ready!</b>\n\n` +
                      `🆔 <b>Message ID:</b> <code>${targetMsgId}</code>\n\n` +
                      `🔗 <b>Direct Stream Link:</b>\n${streamUrl}`;

    if (BOT_TOKEN) {
      const resp = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: replyText,
          parse_mode: 'HTML'
        })
      });
      const resData = await resp.json();
      console.log("🤖 Telegram API Delivery Status:", resData);
    }
  } catch (err) {
    console.error("❌ Error processing webhook event:", err);
  }
});

app.listen(PORT, async () => {
  console.log(`🚀 Server running on port ${PORT}`);

  if (BOT_TOKEN && RENDER_EXTERNAL_URL) {
    try {
      await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${RENDER_EXTERNAL_URL}/bot-webhook`);
      console.log('🤖 Bot Webhook Configured Successfully');
    } catch (e) {
      console.error('Webhook set error:', e);
    }
  }
});
