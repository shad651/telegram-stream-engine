app.post('/bot-webhook', async (req, res) => {
  // Telegram ko instantly OK respond karein
  res.sendStatus(200);

  try {
    const update = req.body;
    console.log("📩 Webhook Event Received:", JSON.stringify(update));

    // Handle both private messages and channel posts/forwards
    const msg = update.message || update.channel_post || update.edited_message;

    if (!msg) {
      console.log("⚠️ Received update with no playable message body.");
      return;
    }

    const chatId = msg.chat.id;
    // Extract message ID from forward header or direct message
    const targetMsgId = msg.forward_from_message_id || msg.message_id;

    const baseUrl = RENDER_EXTERNAL_URL || 'https://telegram-stream-engine.onrender.com';
    const streamUrl = `${baseUrl}/stream?msg_id=${targetMsgId}`;

    const replyText = `🎬 *Video Stream Link Ready!*\n\n` +
                      `🆔 *Message ID:* \`${targetMsgId}\`\n\n` +
                      `🔗 *Direct Stream Link:*\n${streamUrl}`;

    if (BOT_TOKEN) {
      const resp = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: replyText,
          parse_mode: 'Markdown'
        })
      });
      const resData = await resp.json();
      console.log("🤖 Telegram API Delivery Status:", resData);
    } else {
      console.error("❌ BOT_TOKEN environment variable missing.");
    }
  } catch (err) {
    console.error("❌ Error processing webhook event:", err);
  }
});
