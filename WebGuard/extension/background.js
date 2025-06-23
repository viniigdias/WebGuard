chrome.runtime.onInstalled.addListener(() => {
  console.log("Extensão WebGuard instalada.");
});

const whitelist = [ "phishtank.com", "google.com", "facebook.com", "amazon.com", "paypal.com",
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
    "fontawesome.com", "googlefonts.com", "chatgpt.com", "auth.openai.com", "login.microsoftonline.com", "outlook.live.com"];

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    if (!tab.url.startsWith('http://') && !tab.url.startsWith('https://')) {
      console.log('URL ignorada (não HTTP/HTTPS):', tab.url);
      return;
    }
    const domain = new URL(tab.url).hostname;
    if (whitelist.some(w => domain.includes(w))) {
      console.log('URL na whitelist, ignorando:', tab.url);
      return;
    }
    chrome.storage.local.get([tab.url], (result) => {
      if (result[tab.url]) {
        const cached = result[tab.url];
        if (Date.now() - cached.timestamp < 24 * 60 * 60 * 1000) {
          if (cached.result.includes('perigoso') && cached.result.match(/score: \d+\.\d/) && parseFloat(cached.result.match(/score: (\d+\.\d)/)[1]) >= 95) {
            chrome.notifications.create({
              type: 'basic',
              iconUrl: 'assets/WebGuard.png',
              title: 'WEBGUARD Alerta',
              message: '⚠️ Site potencialmente perigoso detectado!'
            });
            console.log('Notificação enviada para:', tab.url, 'Resultado:', cached.result);
          }
          return;
        }
      }
      fetch('http://127.0.0.1:5000/check-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: tab.url })
      })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
        return response.json();
      })
      .then(data => {
        chrome.storage.local.set({
          [tab.url]: { result: data.result, timestamp: Date.now() }
        });
        if (data.result.includes('perigoso') && data.result.match(/score: \d+\.\d/) && parseFloat(data.result.match(/score: (\d+\.\d)/)[1]) >= 95) {
          chrome.notifications.create({
            type: 'basic',
            iconUrl: 'assets/WebGuard.png',
            title: 'WEBGUARD Alerta',
            message: '⚠️ Site potencialmente perigoso detectado!'
          });
          console.log('Notificação enviada para:', tab.url, 'Resultado:', data.result);
        }
      })
      .catch(error => {
        console.error('Erro na verificação:', error);
        chrome.storage.local.set({ [tab.url]: { result: '❌ Erro ao verificar.', timestamp: Date.now() } });
      });
    });
  }
});