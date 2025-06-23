import pytest
import requests
import pandas as pd
import time
import os

@pytest.fixture
def server_url():
    return "http://localhost:5000"

def test_url_phishing_detection(server_url):
    # Verificar se verified_online.csv existe
    csv_path = os.path.join(os.path.dirname(__file__), '../verified_online.csv')
    if os.path.exists(csv_path):
        phishing_urls = pd.read_csv(csv_path)['url'].head(10).tolist()
    else:
        # URLs de fallback
        phishing_urls = ['https://mndot-etzjhi.xin', 'https://mndot-etzjjw.xin']
    
    safe_urls = ['https://google.com', 'https://amazon.com', 'https://microsoft.com']
    
    for url in phishing_urls:
        response = requests.post(f"{server_url}/check-url", json={"url": url})
        print(f"Testando URL {url}: {response.text}")  # Log para depuração
        assert response.status_code == 200, f"Falha na requisição para {url}: {response.text}"
        result = response.json()['result'].lower()
        assert "perigoso" in result or "suspeito" in result, f"Falso negativo detectado: {url}"
    
    for url in safe_urls:
        response = requests.post(f"{server_url}/check-url", json={"url": url})
        print(f"Testando URL {url}: {response.text}")
        assert response.status_code == 200, f"Falha na requisição para {url}: {response.text}"
        result = response.json()['result'].lower()
        assert "seguro" in result or "confiável" in result, f"Falso positivo detectado: {url}"

def test_email_phishing_detection(server_url):
    emails = [
        {
            "subject": "Urgente: Verifique sua conta!",
            "sender": "fake@phish.com",
            "body": "Clique aqui: https://mndot-etzjhi.xin",
            "attachments": ["malware.exe"]
        },
        {
            "subject": "Reunião semanal",
            "sender": "contato@empresa.com",
            "body": "Olá, segue o convite para a reunião.",
            "attachments": []
        }
    ]
    for email in emails:
        response = requests.post(f"{server_url}/check-email", json=email)
        print(f"Testando e-mail {email['subject']}: {response.text}")
        assert response.status_code == 200, f"Falha na requisição para e-mail: {email['subject']}"
        result = response.json()['result'].lower()
        expected = "perigoso" if "fake@phish.com" in email["sender"] else "sem indícios óbvios de phishing"
        assert expected in result, f"Erro na detecção de e-mail: {email['subject']}"

def test_performance(server_url):
    start = time.time()
    for _ in range(100):
        response = requests.post(f"{server_url}/check-url", json={"url": "https://google.com"})
        print(f"Resposta performance: {response.text}")
        assert response.status_code == 200, f"Falha na requisição: {response.text}"
    elapsed = time.time() - start
    assert elapsed < 10, f"Performance lenta: {elapsed}s para 100 verificações"  # Ajustado para 10s