document.getElementById('checkEmailButton').addEventListener('click', async () => {
  const loader = document.getElementById('loader');
  const overlay = document.getElementById('overlay');

  if (!loader || !overlay) {
    console.error('Elementos DOM não encontrados');
    return;
  }

  loader.style.display = 'block';
  overlay.style.display = 'block';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await new Promise(resolve => chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: extractEmailContent
    }, resolve));
    const emailData = results?.[0]?.result || {};
    const { subject = '', sender = '', body = '', attachments = [] } = emailData;
    const emailKey = `${sender}:${subject}`;

    if (!body.trim() && !subject.trim()) {
      throw new Error('Não foi possível capturar o conteúdo do e-mail');
    }

    const cache = await new Promise(resolve => chrome.storage.local.get([emailKey], resolve));
    if (cache[emailKey] && Date.now() - cache[emailKey].timestamp < 24 * 60 * 60 * 1000) {
      updateEmailResult(cache[emailKey].result);
    } else {
      const response = await fetch('http://127.0.0.1:5000/check-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, sender, body, attachments })
      });
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
      const data = await response.json();
      chrome.storage.local.set({ [emailKey]: { result: data.result, timestamp: Date.now() } });
      updateEmailResult(data.result);
    }
  } catch (error) {
    updateEmailResult('❌ Erro ao verificar o e-mail: ' + error.message);
    console.error('Erro na verificação de e-mail:', error);
  }
});

const translations = {
  en: {
    safe: '✅ This site is safe',
    dangerous: '🚨 This site is dangerous',
    error: '❌ Error checking URL'
  },
  pt: {
    safe: '✅ Este site é seguro',
    dangerous: '🚨 Este site é perigoso',
    error: '❌ Erro ao verificar a URL'
  },
  es: {
    safe: '✅ Este sitio es seguro',
    dangerous: '🚨 Este sitio es peligroso',
    error: '❌ Error al verificar la URL'
  }
};

function showPopup(message, type = 'info') {
  const existingPopup = document.querySelector('.email-result-popup');
  if (existingPopup) existingPopup.remove();

  const popup = document.createElement('div');
  popup.classList.add('email-result-popup');
  popup.classList.add(`type-${type}`);
  popup.innerHTML = `
    <div class="popup-content">
      <span class="popup-icon">${type === 'safe' ? '✅' : type === 'dangerous' ? '🚨' : '❌'}</span>
      <p class="popup-message">${message.replace(/\n/g, '<br>')}</p>
      <button class="popup-close-btn" id="popup-close-btn">Fechar</button>
    </div>
  `;
  document.body.appendChild(popup);
  setTimeout(() => popup.classList.add('visible'), 10);

  const closeBtn = popup.querySelector('#popup-close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', closePopup, { once: true });
  } else {
    console.error('Botão Fechar não encontrado');
  }

  const overlay = document.getElementById('overlay');
  if (overlay) overlay.style.display = 'block';

  const loader = document.getElementById('loader');
  if (loader) loader.style.display = 'none';
}

function updatePopup(message, lang = 'pt') {
  const translatedMessage = message.includes('seguro') ? translations[lang].safe :
                            message.includes('perigoso') || message.includes('phishing') ? translations[lang].dangerous :
                            translations[lang].error;
  showPopup(translatedMessage, message.includes('seguro') ? 'safe' :
                             message.includes('perigoso') || message.includes('phishing') ? 'dangerous' : 'error');
}

function updateEmailResult(message, lang = 'pt') {
  const translationsEmail = {
    pt: {
      safe: '✅ Este e-mail parece seguro',
      dangerous: '🚨 Este e-mail é suspeito',
      error: '❌ Erro ao verificar o e-mail'
    }
  };
  let translatedMessage = message.includes('seguro') || (!message.includes('⚠️') && !message.includes('🚨')) ?
    translationsEmail[lang].safe :
    message.includes('suspeito') || message.includes('phishing') || message.includes('⚠️') || message.includes('🚨') ?
    translationsEmail[lang].dangerous : translationsEmail[lang].error;
  showPopup(translatedMessage, message.includes('seguro') ? 'safe' :
                             message.includes('suspeito') || message.includes('phishing') ? 'dangerous' : 'error');
}



function closePopup() {
  const popup = document.querySelector('.email-result-popup');
  if (popup) {
    popup.classList.remove('visible');
    setTimeout(() => {
      popup.remove();
      const overlay = document.getElementById('overlay');
      if (overlay) overlay.style.display = 'none';
      const loader = document.getElementById('loader');
      if (loader) loader.style.display = 'none';
    }, 300);
  }
}

document.getElementById('reportButton').addEventListener('click', () => {
  document.getElementById('reportModal').style.display = 'block';
});

document.getElementById('close-modal').addEventListener('click', () => {
  document.getElementById('reportModal').style.display = 'none';
});

document.getElementById('submit-report').addEventListener('click', async () => {
  const reportType = document.getElementById('report-type').value;
  const comment = document.getElementById('report-comment').value;
  const url = document.getElementById('report-url')?.value || (await chrome.tabs.query({active: true, currentWindow: true}))[0].url;

  const urlPattern = /^(https?:\/\/)?([\w.-]+)\.([a-z]{2,})(\/.*)?$/i;
  if (!urlPattern.test(url)) {
    Swal.fire('Erro', 'URL inválida. Insira uma URL válida.', 'error');
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, report_type: reportType, comment })
    });
    const result = await response.json();
    Swal.fire({
      icon: result.status === 'success' ? 'success' : 'error',
      title: result.status === 'success' ? 'Relatório enviado!' : 'Erro!',
      text: result.message
    });
    document.getElementById('reportModal').style.display = 'none';
  } catch (error) {
    Swal.fire('Erro', 'Falha ao enviar o relatório.', 'error');
  }
});

document.querySelectorAll('a').forEach(btn => {
  btn.addEventListener('mousemove', e => {
    const rect = e.target.getBoundingClientRect();
    const x = e.clientX * 3 - rect.left;
    btn.style.setProperty('--x', x + 'deg');
  });
});

function extractEmailContent() {
  let subject = '', sender = '', body = '', attachments = [];

  const gmBody = document.querySelector('div.a3s');
  const gmSub = document.querySelector('h2.hP');
  const gmSen = document.querySelector('.gD');
  if (gmBody && gmBody.innerText.trim()) body = gmBody.innerText;
  if (gmSub && gmSub.innerText.trim()) subject = gmSub.innerText;
  if (gmSen && (gmSen.getAttribute('email') || gmSen.innerText).trim()) {
    sender = gmSen.getAttribute('email') || gmSen.innerText;
  }

  if (!body) {
    const bodySelectors = [
      'div[role="document"]',
      'div._3Kx2I',
      'div[data-test-id="message-view-body"]',
      'div[aria-label^="Message body"]',
      'div[aria-label^="Conteúdo da mensagem"]'
    ];
    for (let sel of bodySelectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText.trim()) {
        body = el.innerText;
        break;
      }
    }
  }

  if (!sender) {
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    const pageText = document.body.innerText;
    const match = pageText.match(emailRegex);
    if (match) sender = match[0];
  }
  if (!subject) {
    const subjectRegex = /(?:Subject|Assunto):\s*([^\n]+)/i;
    const match = document.body.innerText.match(subjectRegex);
    if (match) subject = match[1].trim();
  }
  if (!body) {
    const bodyRegex = /([\s\S]*?)(?=\n{2,}|$)/;
    const match = document.body.innerText.match(bodyRegex);
    if (match) body = match[1].trim();
  }

  const allAttachments = document.querySelectorAll('div.aQH span.aV3, div[aria-label^="Attachment "] span, div[data-testid="attachment-name"]');
  allAttachments.forEach(att => {
    const fileName = att.innerText.trim();
    if (fileName && !attachments.includes(fileName)) attachments.push(fileName);
  });

  return { subject, sender, body, attachments };
}