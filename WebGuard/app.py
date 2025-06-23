import logging
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from redis import Redis, RedisError
import json
import time
import requests
from bs4 import BeautifulSoup
import tldextract
import base64
import Levenshtein
import ssl
from urllib.parse import urlparse
import socket
import pickle
import pandas as pd
import re
from email.utils import parseaddr
import mysql.connector
from datetime import timedelta

# Configuração de logging
logging.basicConfig(filename='webguard.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar chaves de API
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
VIRUS_TOTAL_API_KEY = os.getenv("VIRUS_TOTAL_API_KEY")
CHECKPHISH_API_KEY = os.getenv("CHECKPHISH_API_KEY")
GOOGLE_SAFE_BROWSING_URL = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_API_KEY}"
VIRUS_TOTAL_URL = "https://www.virustotal.com/api/v3/urls/"

app = Flask(__name__)

try:
    redis_client = Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    logging.info("Connected to Redis successfully")
except RedisError as e:
    logging.error(f"Failed to connect to Redis: {str(e)}")
    redis_client = None

# Configuração do MySQL
def init_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@Gomesdias123",
            database="webguard_db"
        )
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(255) NOT NULL,
                report_type VARCHAR(50) NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("MySQL connection and error_reports table initialized successfully")
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to MySQL: {err}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error initializing database: {str(e)}")
        raise

init_db()

# Lista de domínios legítimos
legitimate_domains = [
    "phishtank.com", "google.com", "facebook.com", "amazon.com", "paypal.com",
    "youtube.com", "instagram.com", "twitter.com", "linkedin.com", "globo.com",
    "uol.com.br", "terra.com.br", "ig.com.br", "mercadolivre.com.br", "banco.br",
    "itaú.com.br", "bradesco.com.br", "santander.com.br", "olx.com.br", "pix.com.br",
    "sebo.com.br", "globoplay.com.br", "netflix.com", "spotify.com", "whatsapp.com",
    "hotmail.com", "outlook.com", "gmail.com", "microsoft.com", "apple.com",
    "grok.com", "x.ai", "unifor.br", "yahoo.com", "bing.com",
    "dropbox.com", "zoom.us", "slack.com", "github.com", "adobe.com",
    "salesforce.com", "cloudflare.com", "trello.com", "ebay.com", "walmart.com",
    "aliexpress.com", "shopify.com", "etsy.com", "target.com", "bestbuy.com",
    "alibaba.com", "chase.com", "wellsfargo.com", "citibank.com", "americanexpress.com",
    "visa.com", "mastercard.com", "stripe.com", "squareup.com", "caixa.gov.br",
    "bb.com.br", "nubank.com.br", "inter.com.br", "americanas.com.br", "submarino.com.br",
    "shopee.com.br", "magazineluiza.com.br", "g1.globo.com", "folha.uol.com.br", "estadao.com.br",
    "gov.br", "mec.gov.br", "receita.fazenda.gov.br", "pucsp.br", "usp.br",
    "telegram.org", "tiktok.com", "snapchat.com", "skype.com", "viber.com",
    "signal.org", "wordpress.com", "medium.com", "reddit.com", "pinterest.com",
    "tumblr.com", "flickr.com", "vimeo.com", "dailymotion.com", "twitch.tv",
    "discord.com", "patreon.com", "kickstarter.com", "indiegogo.com", "booking.com",
    "airbnb.com", "expedia.com", "tripadvisor.com", "uber.com", "lyft.com",
    "didi.com", "agoda.com", "kayak.com", "hilton.com", "marriott.com",
    "ihg.com", "accor.com", "delta.com", "united.com", "aa.com",
    "emirates.com", "qatarairways.com", "lufthansa.com", "britishairways.com", "airfrance.com",
    "klm.com", "latam.com", "gol.com.br", "azul.com.br", "tam.com.br",
    "cvc.com.br", "decolar.com", "samsung.com", "lg.com", "sony.com",
    "panasonic.com", "nokia.com", "motorola.com", "xiaomi.com", "huawei.com",
    "oneplus.com", "oppo.com", "vivo.com", "asus.com", "acer.com",
    "dell.com", "hp.com", "lenovo.com", "intel.com", "amd.com",
    "nvidia.com", "qualcomm.com", "oracle.com", "sap.com", "ibm.com",
    "cisco.com", "vmware.com", "redhat.com", "canonical.com", "ubuntu.com",
    "debian.org", "fedora.org", "opensuse.org", "mozilla.org", "firefox.com",
    "chrome.com", "opera.com", "safari.com", "edge.com", "duckduckgo.com",
    "baidu.com", "yandex.com", "naver.com", "kakao.com", "line.me",
    "zalo.me", "weixin.qq.com", "qq.com", "tencent.com", "sina.com.cn",
    "weibo.com", "jd.com", "taobao.com", "tmall.com", "rakuten.co.jp",
    "yahoo.co.jp", "asahi.com", "yomiuri.co.jp", "mainichi.jp", "nhk.or.jp",
    "japanpost.jp", "sony.co.jp", "panasonic.co.jp", "toyota.com", "honda.com",
    "nissan.com", "mazda.com", "subaru.com", "mitsubishi.com", "suzuki.co.jp",
    "hyundai.com", "kia.com", "volkswagen.com", "bmw.com", "mercedes-benz.com",
    "audi.com", "porsche.com", "ferrari.com", "lamborghini.com", "tesla.com",
    "ford.com", "chevrolet.com", "gm.com", "chrysler.com", "dodge.com",
    "jeep.com", "volvo.com", "peugeot.com", "renault.com", "citroen.com",
    "fiat.com", "skoda-auto.com", "nasa.gov", "esa.int", "cern.ch",
    "who.int", "un.org", "worldbank.org", "imf.org", "wto.org",
    "unesco.org", "unicef.org", "amnesty.org", "hrw.org", "greenpeace.org",
    "wwf.org", "nature.com", "sciencemag.org", "elsevier.com", "springer.com",
    "wiley.com", "tandfonline.com", "ieee.org", "acm.org", "mit.edu",
    "stanford.edu", "harvard.edu", "ox.ac.uk", "cam.ac.uk", "yale.edu",
    "princeton.edu", "columbia.edu", "berkeley.edu", "ucla.edu", "nyu.edu",
    "cornell.edu", "upenn.edu", "uchicago.edu", "caltech.edu", "jhu.edu",
    "duke.edu", "northwestern.edu", "ufrj.br", "ufmg.br", "ufsc.br",
    "ufpe.br", "ufrgs.br", "unicamp.br", "unesp.br", "pucrj.br",
    "fgv.br", "ufba.br", "uol.com", "r7.com", "recordtv.com.br",
    "sbt.com.br", "band.com.br", "redeglobo.com", "cnn.com", "bbc.com",
    "reuters.com", "ap.org", "afp.com", "nytimes.com", "washingtonpost.com",
    "theguardian.com", "wsj.com", "ft.com", "bloomberg.com", "forbes.com",
    "economist.com", "time.com", "newsweek.com", "usatoday.com", "cbsnews.com",
    "abcnews.go.com", "nbcnews.com", "foxnews.com", "aljazeera.com", "dw.com",
    "france24.com", "rt.com", "globo.com.br", "veja.abril.com.br", "epoca.globo.com",
    "cartacapital.com.br", "exame.com", "valor.com.br", "folha.com.br", "correios.com.br",
    "serpro.gov.br", "dataprev.gov.br", "inss.gov.br", "stf.jus.br", "stj.jus.br",
    "tst.jus.br", "trf1.jus.br", "trf2.jus.br", "trf3.jus.br", "trf4.jus.br",
    "trf5.jus.br", "senado.gov.br", "camara.leg.br", "planalto.gov.br", "anatel.gov.br",
    "ans.gov.br", "anvisa.gov.br", "capes.gov.br", "cnpq.br", "finep.gov.br",
    "embrapa.br", "fiocruz.br", "ibge.gov.br", "inep.gov.br", "inpe.br",
    "drogasil.com.br", "raiadrogasil.com.br", "paguemenos.com.br", "extrafarma.com.br", "onofre.com.br",
    "drogaraia.com.br", "ultrafarma.com.br", "boticario.com.br", "natura.com.br", "avon.com.br",
    "marykay.com.br", "sephora.com.br", "loccitane.com.br", "macys.com", "nordstrom.com",
    "jcpenney.com", "kohls.com", "sears.com", "zara.com", "hm.com",
    "uniqlo.com", "gap.com", "oldnavy.com", "bananarepublic.com", "forever21.com",
    "mango.com", "next.com", "marksandspencer.com", "levis.com", "nike.com",
    "adidas.com", "puma.com", "underarmour.com", "reebok.com", "newbalance.com",
    "asics.com", "skechers.com", "vans.com", "converse.com", "timberland.com",
    "dr martens.com", "crocs.com", "supermercadonow.com.br", "carrefour.com.br", "extra.com.br",
    "pao-de-acucar.com.br", "atacadao.com.br", "samsclub.com.br", "walmart.com.br", "casasbahia.com.br",
    "pontofrio.com.br", "ricardoeletro.com.br", "fastshop.com.br", "kabum.com.br", "lenovo.com.br",
    "dell.com.br", "hp.com.br", "samsung.com.br", "lg.com.br", "sony.com.br",
    "panasonic.com.br", "philips.com.br", "electrolux.com.br", "brastemp.com.br", "consul.com.br",
    "fischer.com.br", "mueller.com.br", "tramontina.com.br", "arno.com.br", "oster.com.br",
    "cadence.com.br", "britania.com.br", "polishop.com.br", "cea.com.br", "renner.com.br",
    "riachuelo.com.br", "marisa.com.br", "dafiti.com.br", "kanui.com.br", "netshoes.com.br",
    "centauro.com.br", "decathlon.com.br", "nike.com.br", "adidas.com.br", "puma.com.br",
    "underarmour.com.br", "reebok.com.br", "cvc.com.br", "submarinoviagens.com.br", "viacosteira.com.br",
    "hurb.com", "123milhas.com.br", "voeazul.com.br", "voegol.com.br", "latamairlines.com",
    "tap.pt", "avianca.com.br", "passagensaereas.com.br", "voeja.com.br", "edestinos.com.br",
    "maxmilhas.com.br", "skyscanner.com.br", "google.com.br", "yahoo.com.br", "bing.com.br",
    "duckduckgo.com.br", "uol.com.br", "bol.com.br", "msn.com", "aol.com",
    "protonmail.com", "mail.com", "zoho.com", "gmx.com", "icloud.com",
    "me.com", "mac.com", "ebay.com.br", "mercadolivre.com", "olx.com",
    "vivareal.com.br", "zapimoveis.com.br", "quintoandar.com.br", "imovelweb.com.br", "trovit.com.br",
    "wimoveis.com.br", "chavesnamao.com.br", "airbnb.com.br", "booking.com.br", "trivago.com.br",
    "hoteis.com", "expedia.com.br", "decolar.com.br", "cvc.com", "submarino.com",
    "americanas.com", "shopee.com", "aliexpress.com.br", "wish.com", "gearbest.com",
    "banggood.com", "dx.com", "lightinthebox.com", "minilinthebox.com", "shein.com",
    "romwe.com", "asos.com", "boohoo.com", "missguided.com", "prettylittlething.com",
    "nastygal.com", "zalando.com", "aboutyou.com", "yoox.com", "farfetch.com",
    "net-a-porter.com", "matchesfashion.com", "ssense.com", "revolve.com", "shopbop.com",
    "urbanoutfitters.com", "anthropologie.com", "freepeople.com", "bhldn.com", "modcloth.com",
    "lulus.com", "dsw.com", "zappos.com", "footlocker.com", "finishline.com",
    "jd sports.com", "champssports.com", "courir.com", "size.co.uk", "sneakernews.com",
    "goat.com", "stockx.com", "kickscrew.com", "flightclub.com", "stadiumgoods.com",
    "grailed.com", "depop.com", "vestiairecollective.com", "therealreal.com", "poshmark.com",
    "thredup.com", "tradesy.com", "ebay.co.uk", "amazon.co.uk", "amazon.de",
    "amazon.fr", "amazon.it", "amazon.es", "amazon.co.jp", "amazon.in",
    "amazon.com.au", "amazon.ca", "amazon.com.mx", "amazon.com.br", "flipkart.com",
    "snapdeal.com", "myntra.com", "jabong.com", "paytm.com", "bigbasket.com",
    "grofers.com", "jiomart.com", "dmart.in", "reliancefresh.com", "spencers.in",
    "starbazaar.in", "tesco.com", "sainsburys.co.uk", "asda.com", "morrisons.com",
    "waitrose.com", "ocado.com", "aldi.co.uk", "lidl.co.uk", "coop.co.uk",
    "iceland.co.uk", "kroger.com", "safeway.com", "albertsons.com", "publix.com",
    "wholefoodsmarket.com", "traderjoes.com", "costco.com", "samsclub.com", "bjwholesale.com",
    "instacart.com", "doordash.com", "ubereats.com", "grubhub.com", "postmates.com",
    "deliveroo.com", "justeat.com", "zomato.com", "swiggy.com", "foodpanda.com",
    "ifood.com.br", "rappi.com.br", "uber.com.br", "99app.com", "cabify.com",
    "bolt.eu", "freenow.com", "getir.com", "glovoapp.com", "yandex.taxi",
    "didi.com.br", "inDriver.com", "lyft.com.br", "trip.com", "ctrip.com",
    "makemytrip.com", "yatra.com", "cleartrip.com", "goibibo.com", "agoda.com.br",
    "kayak.com.br", "momondo.com", "cheapflights.com", "priceline.com", "hotwire.com",
    "orbitz.com", "travelocity.com", "lonelyplanet.com", "roughguides.com", "frommers.com",
    "fodors.com", "wikitravel.org", "tripit.com", "wanderlog.com", "rome2rio.com",
    "viator.com", "getyourguide.com", "klook.com", "musement.com", "toursbylocals.com",
    "airbnb.com/experiences", "expatexchange.com", "internations.org", "meetup.com", "eventbrite.com",
    "ticketmaster.com", "livenation.com", "stubhub.com", "seatgeek.com", "vividseats.com",
    "axs.com", "tixr.com", "songkick.com", "bandsintown.com", "residentadvisor.net",
    "dICE.com", "tidal.com", "deezer.com", "pandora.com", "iheart.com",
    "soundcloud.com", "bandcamp.com", "last.fm", "mixcloud.com", "qobuz.com",
    "napster.com", "yandex.music", "vk.com", "ok.ru", "mail.ru",
    "rambler.ru", "lenta.ru", "ria.ru", "tass.com", "kommersant.ru",
    "rbc.ru", "gazeta.ru", "fontanka.ru", "kp.ru", "aif.ru",
    "iz.ru", "vedomosti.ru", "meduza.io", "themoscowtimes.com", "rtve.es",
    "elpais.com", "elmundo.es", "abc.es", "lavanguardia.com", "lemonde.fr",
    "lefigaro.fr", "liberation.fr", "lci.fr", "bfmtv.com", "corriere.it",
    "repubblica.it", "lastampa.it", "ilsole24ore.com", "ansa.it", "sueddeutsche.de",
    "faz.net", "welt.de", "spiegel.de", "zeit.de", "t-online.de",
    "bild.de", "focus.de", "heise.de", "golem.de", "chip.de",
    "cnet.com", "theverge.com", "techcrunch.com", "engadget.com", "wired.com",
    "arstechnica.com", "zdnet.com", "techradar.com", "pcmag.com", "tomshardware.com",
    "anandtech.com", "digitaltrends.com", "gizmodo.com", "mashable.com", "venturebeat.com",
    "thenextweb.com", "techrepublic.com", "gamespot.com", "ign.com", "polygon.com",
    "kotaku.com", "eurogamer.net", "pcgamer.com", "rockpapershotgun.com", "gameinformer.com",
    "destructoid.com", "gamesradar.com", "steampowered.com", "epicgames.com", "origin.com",
    "ubisoft.com", "ea.com", "activision.com", "blizzard.com", "bethesda.net",
    "square-enix.com", "capcom.com", "sega.com", "konami.com", "bandainamco.com",
    "nintendo.com", "playstation.com", "xbox.com", "riotgames.com", "valvesoftware.com",
    "unity.com", "unrealengine.com", "autodesk.com", "blender.org", "adobe.com/br",
    "canva.com", "figma.com", "sketch.com", "invisionapp.com", "dribbble.com",
    "behance.net", "deviantart.com", "artstation.com", "500px.com", "shutterstock.com",
    "gettyimages.com", "istockphoto.com", "unsplash.com", "pexels.com", "pixabay.com",
    "freepik.com", "flaticon.com", "thenounproject.com", "iconfinder.com", "icons8.com",
    "fontawesome.com", "googlefonts.com", "chatgpt.com", "auth.openai.com", "login.microsoftonline.com", "login.microsoftonline.com", "outlook.live.com"
]

def is_similar_to_legitimate_domain(domain):
    for legit_domain in legitimate_domains:
        if Levenshtein.distance(domain, legit_domain) <= 2:
            return True
    return False

def check_ssl(url):
    parsed_url = urlparse(url)
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=parsed_url.hostname) as s:
            s.connect((parsed_url.hostname, 443))
        return True
    except Exception as e:
        logging.warning(f"SSL check failed for {url}: {str(e)}")
        return False

def check_html_for_suspicious_elements(soup, url):
    trusted_domains = ['youtube.com', 'gmail.com', 'google.com', 'facebook.com']
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if any(trusted_domain in domain for trusted_domain in trusted_domains):
        return False
    if soup.find_all('iframe') or soup.find_all('script', {'src': True}):
        return True
    return False

def check_url_google(url):
    try:
        payload = {
            "client": {"clientId": "webguard", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        response = requests.post(GOOGLE_SAFE_BROWSING_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "matches" in data:
            threat_types = [match["threatType"] for match in data["matches"]]
            return f"🚨 Este site é **perigoso** segundo o Google Safe Browsing! Ameaças detectadas: {', '.join(threat_types)}", 100
        return "✅ Este site parece seguro segundo o Google Safe Browsing.", 0
    except requests.RequestException as e:
        logging.error(f"Google Safe Browsing error for {url}: {str(e)}")
        return f"❌ Erro ao verificar com Google Safe Browsing: {str(e)}", 0

def check_url_virustotal(url):
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        headers = {"x-apikey": VIRUS_TOTAL_API_KEY}
        response = requests.get(VIRUS_TOTAL_URL + url_id, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "data" in data and data["data"]["attributes"]["last_analysis_stats"]["malicious"] > 0:
            return "⚠️ Este site é **perigoso** segundo o VirusTotal!", 100
        return "✅ Este site parece seguro segundo o VirusTotal.", 0
    except requests.RequestException as e:
        logging.error(f"VirusTotal error for {url}: {str(e)}")
        return f"❌ Erro ao verificar com VirusTotal: {str(e)}", 0

def check_url_checkphish(url):
    try:
        endpoint = "https://api.checkphish.ai/scan"
        headers = {"Authorization": f"Bearer {CHECKPHISH_API_KEY}"}
        payload = {"url": url}
        response = requests.post(endpoint, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("is_phishing"):
            return "⚠️ Este site está listado como phishing pelo CheckPhish!", 100
        return "✅ Esta URL não está registrada como phishing pelo CheckPhish.", 0
    except requests.RequestException as e:
        logging.error(f"CheckPhish error for {url}: {str(e)}")
        return f"❌ Erro ao verificar com CheckPhish: {str(e)}", 0

def load_model():
    try:
        with open('url_classifier_model.pkl', 'rb') as file:
            model = pickle.load(file)
        logging.info("Machine learning model loaded successfully")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        raise

def predict_url_safety(url, model):
    try:
        ext = tldextract.extract(url)
        domain = ext.domain
        length_domain = len(url)
        subdomains_count = url.count('.')
        contains_https = 1 if url.startswith('https://') else 0
        contains_login_form = 1 if "login" in url.lower() else 0
        contains_redirect = 1 if "redirect" in url.lower() else 0
        special_chars = len(re.findall(r'[%\-_=+/?]', url))
        path_depth = len(url.split('/')) - 3

        features = pd.DataFrame([{
            'length_domain': length_domain,
            'subdomains_count': subdomains_count,
            'contains_https': contains_https,
            'contains_login_form': contains_login_form,
            'contains_redirect': contains_redirect,
            'special_chars': special_chars,
            'path_depth': path_depth
        }])

        prediction = model.predict(features)[0]
        if prediction == 1:
            return "⚠️ Esta URL é um site de **phishing**.", 80
        return "✅ Esta URL é segura.", 0
    except Exception as e:
        logging.error(f"ML prediction error for {url}: {str(e)}")
        return f"❌ Erro na predição de ML: {str(e)}", 0

def check_url(url):
    try:
        logging.info(f"Checking URL: {url}")
        model = load_model()
        ext = tldextract.extract(url)
        domain = ext.domain + '.' + ext.suffix
        full_domain = ext.subdomain + '.' + domain if ext.subdomain else domain
        # Logar domínio extraído
        logging.info(f"Extracted domain: {full_domain}")
        # Verificar domínio e subdomínios na whitelist
        for legit_domain in legitimate_domains:
            if full_domain.lower() == legit_domain.lower() or full_domain.lower().endswith('.' + legit_domain.lower()):
                logging.info(f"URL {url} matches whitelist domain: {legit_domain}")
                return "✅ Este site é confiável (whitelist)."

        results = []
        weights = {'google': 0.4, 'virustotal': 0.35, 'checkphish': 0.3, 'ml': 0.005}  # ML minimizado
        google_result, google_score = check_url_google(url)
        results.append(google_result)
        scores = [google_score * weights['google']]

        virustotal_result, virustotal_score = check_url_virustotal(url)
        results.append(virustotal_result)
        scores.append(virustotal_score * weights['virustotal'])

        checkphish_result, checkphish_score = check_url_checkphish(url)
        results.append(checkphish_result)
        scores.append(checkphish_score * weights['checkphish'])

        ml_result, ml_score = predict_url_safety(url, model)
        results.append(ml_result)
        scores.append(ml_score * weights['ml'])

        confidence_score = sum(scores) * 100
        if confidence_score >= 95:  # Limiar mantido
            return f"🚨 Este site é perigoso (score: {confidence_score:.1f}).\nDetalhes:\n" + "\n".join(results)
        if confidence_score >= 70:  # Limiar mantido
            return f"⚖️ Este site é suspeito (score: {confidence_score:.1f}).\nDetalhes:\n" + "\n".join(results)

        return f"✅ Este site parece seguro (score: {confidence_score:.1f}).\nDetalhes:\n" + "\n".join(results)
    except Exception as e:
        logging.error(f"Error checking URL {url}: {str(e)}")
        return f"❌ Erro ao verificar: {str(e)}"


@app.route('/check-url', methods=['POST'])
def check_url_api():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            raise ValueError("No URL provided in request")
        url = data['url']
        logging.info(f"API request for URL: {url}")
        
        # Limpar cache para garantir resultados atualizados
        if redis_client:
            redis_client.delete(url)
            logging.info(f"Cache cleared for {url}")
        
        result = check_url(url)
        
        if redis_client:
            redis_client.setex(url, 24 * 3600, json.dumps({'result': result}))
            logging.info(f"Cache set for {url}")
        
        return jsonify({'result': result})
    except Exception as e:
        logging.error(f"Error in /check-url API: {str(e)}")
        return jsonify({'error': f'Erro ao verificar URL: {str(e)}'}), 500
    
    
# Dicionário de frases de phishing e seus pesos
PHISH_KEYWORDS = {
    "senha": 1,
    "verifique sua conta": 2,
    "clique aqui": 1,
    "urgente": 1,
    "atualize seu cadastro": 2,
    "limite expirado": 2,
    "confirme sua identidade": 2,
    "acesso bloqueado": 2,
    "você ganhou": 1,
    "fatura vencida": 1,
    "problema na sua conta": 2,
    "ação necessária": 1
}

def check_suspicious_patterns(text: str) -> list:
    results = []
    text = text.lower()
    if re.search(r'!{3,}', text):
        results.append("⚠️ Excesso de pontos de exclamação detectado (ex.: '!!!').")
    for shortener in URL_SHORTENERS:
        if shortener in text:
            results.append(f"🚨 Link encurtado detectado ({shortener}) - alta probabilidade de phishing.")
    return results


# Lista de extensões de anexos suspeitas
SUSPICIOUS_EXTENSIONS = ['.exe', '.bat', '.scr', '.com', '.pif', '.vbs', '.js', '.wsf', '.lnk']

# Lista de domínios de encurtadores de URL conhecidos
URL_SHORTENERS = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly']

def keyword_score(text: str) -> int:
    """Retorna um score de suspeita com base em PHISH_KEYWORDS."""
    text = text.lower()
    score = 0
    for phrase, weight in PHISH_KEYWORDS.items():
        if phrase in text:
            score += weight
    return score


def check_attachments(attachments: list) -> list:
    results = []
    for attachment in attachments:
        # Extrair a extensão do arquivo (se houver)
        _, ext = os.path.splitext(attachment.lower())
        if ext in SUSPICIOUS_EXTENSIONS:
            results.append(f"⚠️ Anexo suspeito detectado: {attachment} (extensão {ext} é potencialmente perigosa).")
    return results

def sender_domain(sender: str) -> tuple:
    addr = parseaddr(sender)[1]
    domain = addr.split("@")[-1] if "@" in addr else ""
    results = []
    if not domain:
        return domain, ["🚨 Remetente não identificado (sem endereço de e-mail válido)."]
    if domain.lower() in [d.lower() for d in legitimate_domains]:
        return domain, []
    if is_similar_to_legitimate_domain(domain):
        results.append(f"🚨 Domínio do remetente ({domain}) é muito semelhante a um domínio legítimo (possível spoofing).")
    else:
        results.append(f"⚠️ Domínio do remetente ({domain}) não é reconhecido como confiável.")
    return domain, results

def check_attachment_virustotal(attachment_name: str, attachment_content: bytes = None) -> tuple:
    try:
        if not attachment_content:
            return f"❌ Nenhum conteúdo de anexo fornecido para {attachment_name}.", 0
        headers = {"x-apikey": VIRUS_TOTAL_API_KEY}
        files = {"file": (attachment_name, attachment_content)}
        response = requests.post("https://www.virustotal.com/api/v3/files", headers=headers, files=files, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "data" in data and data["data"]["attributes"]["last_analysis_stats"]["malicious"] > 0:
            return f"🚨 Anexo malicioso detectado: {attachment_name}.", 100
        return f"✅ Anexo seguro: {attachment_name}.", 0
    except requests.RequestException as e:
        logging.error(f"VirusTotal attachment error for {attachment_name}: {str(e)}")
        return f"❌ Erro ao verificar anexo com VirusTotal: {str(e)}", 0

@app.route('/check-email', methods=['POST'])
def check_email_api():
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        sender = data.get('sender', '')
        body = data.get('body', '')
        attachments = data.get('attachments', [])
        if not (subject or body):
            return jsonify({'result': '❌ Nenhum conteúdo de e-mail fornecido.'})

        total_score = keyword_score(subject + " " + body)
        urls = re.findall(r'(https?://[^\s"<]+)', body)
        send_dom, sender_results = sender_domain(sender)
        results = sender_results

        if not send_dom:
            results.append("🚨 E-mail potencialmente phishing: Remetente não identificado.")

        for url in urls:
            url_result = check_url(url)
            results.append(f"{url} -> {url_result}")
            if "perigoso" in url_result or "suspeito" in url_result:
                results.append(f"🚨 E-mail contém link malicioso ({url}).")
                total_score += 10
            link_dom = re.sub(r"^https?://", "", url).split('/')[0]
            if send_dom and send_dom.lower() not in link_dom.lower():
                results.append(f"⚠️ Domínio do link ({link_dom}) não corresponde ao remetente ({send_dom}).")
                total_score += 5

        suspicious_patterns = check_suspicious_patterns(subject + " " + body)
        results.extend(suspicious_patterns)
        if suspicious_patterns:
            total_score += 5

        attachment_results = check_attachments(attachments)
        for attachment in attachments:
            attachment_result, attachment_score = check_attachment_virustotal(attachment, attachment.encode())
            results.append(attachment_result)
            if "malicioso" in attachment_result:
                total_score += 10
        results.extend(attachment_results)

        if total_score >= 5 or any("🚨" in r for r in results):
            results.append("🚨 E-mail identificado como phishing.")
        elif (not urls and total_score == 0 and not attachment_results and not suspicious_patterns and
              send_dom and not any("suspeito" in r or "phishing" in r for r in sender_results)):
            results.append("✅ E-mail sem indícios de phishing.")
        else:
            results.append("⚠️ E-mail suspeito, recomenda-se cautela.")

        return jsonify({'result': "\n".join(results)})

    except Exception as e:
        return jsonify({'result': f'Erro ao verificar e-mail: {str(e)}'})
    
    
@app.route('/report', methods=['POST'])
def report_error():
    try:
        data = request.get_json()
        url = data.get('url')
        report_type = data.get('report_type')
        comment = data.get('comment')

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@Gomesdias123",
            database="webguard_db"
        )
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO error_reports (url, report_type, comment)
            VALUES (%s, %s, %s)
        ''', (url, report_type, comment))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Relatório enviado com sucesso!'})

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Erro ao enviar o relatório: {str(err)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao enviar o relatório: {str(e)}'})

@app.route('/', methods=['GET'])
def test_server():
    return jsonify({'message': 'Servidor WebGuard está rodando com sucesso!'})

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)