/**
 * Cloudflare Email Worker
 * 接收邮件并转发到本地 Python 服务器
 */

export default {
  // Email 处理器
  async email(message, env, ctx) {
    console.log('📧 收到邮件:', message.from, '->', message.to);
    
    try {
      // 读取邮件内容
      const rawEmail = await streamToString(message.raw);
      const subject = message.headers.get('subject') || 'No Subject';
      
      console.log('主题:', subject);
      
      // 构建邮件数据
      const emailData = {
        to: message.to,
        from: message.from,
        subject: subject,
        text: rawEmail,
        html: rawEmail
      };
      
      // 转发到本地服务器
      // 注意：需要使用 Cloudflare Tunnel 的公网地址
      const localServerUrl = env.LOCAL_SERVER_URL || 'http://localhost:5000/email';
      
      console.log('转发到:', localServerUrl);
      
      const response = await fetch(localServerUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(emailData)
      });
      
      if (response.ok) {
        console.log('✅ 邮件已转发');
      } else {
        console.error('❌ 转发失败:', response.status, await response.text());
      }
      
      // 可选：同时发送到 Gotify
      if (env.GOTIFY_URL && env.GOTIFY_TOKEN) {
        await sendToGotify(env, subject, rawEmail);
      }
      
    } catch (error) {
      console.error('❌ 处理邮件失败:', error.message);
      console.error(error.stack);
    }
  },
  
  // 可选：HTTP 处理器（用于测试）
  async fetch(request, env, ctx) {
    return new Response(JSON.stringify({
      status: 'ok',
      message: 'Email Worker is running',
      timestamp: new Date().toISOString()
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

/**
 * 将 Stream 转换为字符串
 */
async function streamToString(stream) {
  const reader = stream.getReader();
  const chunks = [];
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  
  const uint8Array = new Uint8Array(
    chunks.reduce((acc, chunk) => acc + chunk.length, 0)
  );
  
  let offset = 0;
  for (const chunk of chunks) {
    uint8Array.set(chunk, offset);
    offset += chunk.length;
  }
  
  return new TextDecoder('utf-8').decode(uint8Array);
}

/**
 * 发送到 Gotify（可选）
 */
async function sendToGotify(env, subject, content) {
  try {
    // 提取验证链接
    const linkMatch = content.match(
      /https:\/\/services\.sheerid\.com\/verify\/[^\s<>"]+emailToken=\d+/
    );
    const verificationLink = linkMatch ? linkMatch[0] : '';
    
    await fetch(`${env.GOTIFY_URL}/message?token=${env.GOTIFY_TOKEN}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: '📧 SheerID 验证邮件',
        message: `主题: ${subject}\n\n${verificationLink || '无验证链接'}`,
        priority: 8
      })
    });
    
    console.log('✅ 已发送 Gotify 通知');
  } catch (error) {
    console.error('❌ Gotify 通知失败:', error.message);
  }
}
