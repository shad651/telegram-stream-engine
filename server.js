require('dotenv').config();
const express = require('express');
const { TelegramClient } = require('telegram');
const { StringSession } = require('telegram/sessions');
const { Readable } = require('stream');

// ---------- Configuration ----------
const {
  TELEGRAM_API_ID,
  TELEGRAM_API_HASH,
  TELEGRAM_SESSION,
  TELEGRAM_CHANNEL_ID,
  PORT = 3000,
} = process.env;

if (!TELEGRAM_API_ID || !TELEGRAM_API_HASH || !TELEGRAM_SESSION || !TELEGRAM_CHANNEL_ID) {
  console.error('❌ Missing required environment variables.');
  process.exit(1);
}

// ---------- Telegram Client (singleton) ----------
let client = null;

async function getTelegramClient() {
  if (client) return client;

  client = new TelegramClient(
    new StringSession(TELEGRAM_SESSION),
    Number(TELEGRAM_API_ID),
    TELEGRAM_API_HASH,
    { connectionRetries: 5 }
  );

  await client.start();
  console.log('✅ Telegram client connected.');
  return client;
}

// ---------- Express App ----------
const app = express();

// Health check
app.get('/health', (req, res) => res.send('OK'));

// Stream endpoint
app.get('/stream', async (req, res) => {
  const msgId = req.query.msg_id;
  if (!msgId) {
    return res.status(400).json({ error: 'Missing msg_id parameter' });
  }

  try {
    const client = await getTelegramClient();
    const channelId = Number(TELEGRAM_CHANNEL_ID);

    // 1. Fetch message
    const messages = await client.getMessages(channelId, { ids: [Number(msgId)] });
    const message = messages[0];
    if (!message) {
      return res.status(404).json({ error: 'Message not found' });
    }

    // 2. Verify it's a video
    const media = message.media;
    if (!media || !media.document || !media.document.mimeType?.startsWith('video/')) {
      return res.status(400).json({ error: 'Message does not contain a video' });
    }

    const fileSize = media.document.size;
    const mimeType = media.document.mimeType || 'video/mp4';

    // 3. Parse Range header
    const rangeHeader = req.headers.range;
    let start = 0;
    let end = fileSize - 1;
    let statusCode = 200;

    if (rangeHeader) {
      const parts = rangeHeader.replace(/bytes=/, '').split('-');
      start = parseInt(parts[0], 10);
      end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      if (start > end || start >= fileSize) {
        return res.status(416).json({ error: 'Requested range not satisfiable' });
      }
      statusCode = 206;
    }

    // 4. Set response headers
    const contentLength = end - start + 1;
    res.status(statusCode);
    res.setHeader('Content-Type', mimeType);
    res.setHeader('Accept-Ranges', 'bytes');
    res.setHeader('Content-Length', contentLength);
    res.setHeader('Content-Range', `bytes ${start}-${end}/${fileSize}`);
    res.setHeader('Cache-Control', 'no-cache');

    // 5. Create a readable stream from Telegram media
    //    We'll download only the requested range if possible,
    //    but GramJS `downloadMedia` doesn't support byte ranges natively.
    //    As a workaround we download the whole file and pipe it,
    //    but we can still limit the bytes sent to the client.
    //    However, to truly save bandwidth we would need to seek in the file.
    //    Since GramJS does not support range download, we download full file
    //    but we pipe only the requested slice to the client.
    //    For a production system consider a caching layer or use a custom
    //    implementation with `client.downloadMedia` with a writable stream
    //    that discards bytes before `start` and stops after `end`.

    const outputStream = new Readable({
      read() {} // no-op, we push data manually
    });

    // We'll create a custom writable stream that filters bytes
    const filterStream = new (require('stream').Transform)({
      transform(chunk, encoding, callback) {
        // We need to track current position relative to file start
        // This is tricky because we don't know the offset in the stream.
        // A simpler approach: download the entire file, then slice the buffer.
        // But that defeats low memory usage.
        // Instead, we can use `client.downloadMedia` with `outputStream` being
        // a custom writable that discards bytes outside [start, end].
        // We'll implement a byte filter as a Transform stream.
        // We'll keep a global offset variable.

        // Since we're using a Transform, we need to keep state.
        // We'll use a closure with `this.bytesWritten` or similar.
        // But simpler: we'll not use the Transform approach; we'll download
        // into a temp file and then stream range? Not ideal.
        // The most memory-efficient way with GramJS is to use
        // `client.downloadMedia(message, { outputFile: writableStream })`
        // and provide a custom writable that only stores the needed range.
        // We can implement a writable that writes only if within range.

        // === RECOMMENDED APPROACH (Memory efficient) ===
        // We'll create a custom Writable stream that writes bytes to a buffer
        // only for the requested range. But we must know the offset.
        // Since the download stream is sequential, we can count bytes.
        // Let's implement it below.
      }
    });

    // Instead of the above complex Transform, I'll present a clean solution:
    // Use a custom writable that tracks bytes and pushes to the response.
    // We'll create a "range writable" that writes to a buffer and then
    // to response when ready, but we want to stream to response immediately.
    // Actually, we can create a PassThrough stream and pipe the download
    // to it, then we use a Transform stream that drops bytes outside range.
    // That Transform will keep an internal counter.

    // ---------- Implementation with Transform (low memory) ----------
    const { Transform } = require('stream');
    let bytesWritten = 0;
    let bytesSent = 0;

    const rangeFilter = new Transform({
      transform(chunk, encoding, callback) {
        const chunkSize = chunk.length;
        const chunkStart = bytesWritten;
        const chunkEnd = bytesWritten + chunkSize - 1;
        bytesWritten += chunkSize;

        // Check if this chunk overlaps the requested range
        if (chunkEnd < start || chunkStart > end) {
          // No overlap, discard
          return callback();
        }

        // Calculate slice offsets within this chunk
        const sliceStart = Math.max(0, start - chunkStart);
        const sliceEnd = Math.min(chunkSize - 1, end - chunkStart);
        const slice = chunk.subarray(sliceStart, sliceEnd + 1);

        bytesSent += slice.length;
        this.push(slice);
        callback();
      },
      // We need to flush any remaining data? Not necessary.
    });

    // Now pipe the download into the rangeFilter, then to response
    // But we need to handle downloadMedia with a writable stream.
    // We can create a PassThrough stream and pipe it.
    const passThrough = new (require('stream').PassThrough)();

    // We'll start the download asynchronously and pipe to passThrough
    // We need to catch errors.
    const downloadPromise = client.downloadMedia(message, {
      outputStream: passThrough,
      // Optional: progress callback
    });

    // Pipe through range filter and then to response
    passThrough
      .pipe(rangeFilter)
      .pipe(res)
      .on('error', (err) => {
        console.error('Stream error:', err);
        if (!res.headersSent) res.status(500).end();
      });

    // Wait for download to finish (or error)
    try {
      await downloadPromise;
      // When download completes, end the response if not already ended
      if (!res.writableEnded) res.end();
    } catch (downloadErr) {
      console.error('Download error:', downloadErr);
      if (!res.headersSent) {
        res.status(500).json({ error: 'Failed to download media' });
      } else {
        res.destroy(downloadErr);
      }
    }

    // Clean up on client abort
    req.on('aborted', () => {
      passThrough.destroy();
      rangeFilter.destroy();
    });

  } catch (err) {
    console.error('Stream error:', err);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error' });
    } else {
      res.end();
    }
  }
});

// ---------- Start Server ----------
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`   Stream endpoint: http://localhost:${PORT}/stream?msg_id=<id>`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
  if (client) await client.disconnect();
  process.exit(0);
});
