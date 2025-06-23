# 🛡️ WebGuard

**WebGuard** é uma extensão de navegador anti-phishing desenvolvida como Trabalho de Conclusão de Curso (TCC), com o objetivo de **proteger usuários contra ataques de phishing** em URLs e e-mails. Utilizando machine learning, múltiplas APIs de segurança e um backend leve com Flask, a ferramenta oferece proteção em tempo real com interface amigável.

## 📌 Objetivo

Reduzir a exposição de usuários e pequenas empresas a ataques de phishing por meio de uma solução acessível, leve e eficaz — integrando detecção inteligente de URLs e e-mails maliciosos com base em modelos de machine learning e fontes confiáveis.

---

## 🚀 Funcionalidades

- ✅ Verificação automática de URLs em tempo real.
- 📧 Análise de e-mails (remetente, assunto, anexos, corpo) no Gmail e Outlook.
- 📊 Relatórios de falsos positivos e negativos.
- 🔔 Notificações interativas para URLs perigosas.
- 🧠 Classificação com modelo RandomForest treinado com +30.000 exemplos.
- 🌐 Integração com Google Safe Browsing, VirusTotal e PhishTank.

---

## 🏗️ Arquitetura do Projeto

webguard/
├── extension/
│ ├── assets/
│ ├── background.js
│ ├── content.js
│ ├── manifest.json
│ ├── popup.html
│ ├── popup.js
│ ├── style.css
│ └── sweetalert2.all.min.js
├── app.py # Backend Flask
├── train_model.py # Treinamento ML
├── dataset_phishing_and_security.csv
├── url_classifier_model.pkl # Modelo RandomForest
├── requirements.txt
└── README.md

---

## ⚙️ Tecnologias Utilizadas

- **Frontend:** JavaScript, HTML, CSS, SweetAlert2
- **Backend:** Python (Flask)
- **Banco de Dados:** MySQL
- **Machine Learning:** TensorFlow, Scikit-learn (RandomForest)
- **APIs de Segurança:** Google Safe Browsing, VirusTotal, PhishTank
- **Testes:** Jest (JS), Pytest (Python), Postman (integração)
- **CI/CD:** GitHub Actions
- **Monitoramento:** Logs Flask + Kibana, métricas com Prometheus

---

## 🧪 Trechos de Código (Exemplos Críticos)

**🔍 Verificação de URL no backend Flask:**

```python
@app.route('/check-url', methods=['POST'])
def check_url_api():
    data = request.get_json()
    url = data.get('url')
    model = load_model()
    # Verificação sequencial com 3 APIs + ML
    if "perigoso" in check_url_google(url):
        return jsonify({'result': 'phishing-google'})
    if "perigoso" in check_url_virustotal(url):
        return jsonify({'result': 'phishing-virustotal'})
    if "phishing" in check_url_phishtank(url):
        return jsonify({'result': 'phishing-phishtank'})
    return jsonify({'result': predict_url_safety(url, model)})


📬 Extração de conteúdo de e-mails no popup.js:

function extractEmailContent() {
    let subject = '', sender = '', body = '', attachments = [];
    const gmBody = document.querySelector('div.a3s');
    if (gmBody && gmBody.innerText.trim()) body = gmBody.innerText;
    const match = document.body.innerText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
    if (match) sender = match[0];
    return { subject, sender, body, attachments };
}



✅ Como Instalar (Modo Desenvolvedor)
1.Clone o repositório:

git clone https://github.com/viniigdias/WebGuard.git

2.Acesse chrome://extensions/ no Chrome.

3.Ative o Modo Desenvolvedor (canto superior direito).

4.Clique em "Carregar sem compactação" e selecione a pasta webguard/extension.

5.A extensão será adicionada e estará pronta para uso.


📈 Resultados e Métricas:

| Indicador                    | Valor                |
| ---------------------------- | -------------------- |
| Latência média (URL)         | 400ms                |
| Latência média (E-mail)      | 600ms                |
| Throughput no servidor Flask | 2000 requisições/min |
| Cobertura de código          | 95%                  |
| Custo x Netcraft             | -40%                 |


🛠️ Próximas Funcionalidades
Suporte a Yahoo Mail e mais provedores.

Verificação de anexos de e-mails.

Painel de administração com métricas.

Suporte a Firefox

Integração com APIs WHOIS e reputação de domínios.

Tradução multilíngue da interface.

📚 Créditos e Informações
Autor: Vinicius Gomes Dias — RA 2217696

Período do projeto: 20/03/2025 a 06/06/2025

Instituição: Universidade de Fortaleza

Repositório Oficial: github.com/viniigdias/WebGuard

