const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

(async () => {
  console.log("Browser launch ho raha hai...");
  
  // Termux/Linux ke liye headless mode zaroori hai
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();

  // User-agent set karna taaki real browser lage
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  // Network request sniffer
  page.on('request', request => {
    const url = request.url();
    if (url.includes('.m3u8') || url.includes('.mp4') || url.includes('playlist')) {
      console.log('\n[!] Target Video Stream Link Mil Gaya:');
      console.log(url);
    }
  });

  try {
    // Soap2day ya clone ka URL yahan dalein
    const targetUrl = 'https://soap2day.pe/'; // (Example URL)
    console.log(`Page load ho raha hai: ${targetUrl}`);
    
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 60000 });
    
    console.log("Page khul gaya, links ke liye wait kar rahe hain...");
    await new Promise(resolve => setTimeout(resolve, 10000)); // 10 seconds wait

  } catch (error) {
    console.error("Error aa gaya:", error.message);
  } finally {
    await browser.close();
    console.log("Browser band ho gaya.");
  }
})();
