import re
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import pickle
import tldextract
import logging

# Configurar logging
logging.basicConfig(filename='train_model.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_features(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    try:
        ext = tldextract.extract(url)
        domain = ext.domain
        length_domain = len(url)
        subdomains_count = url.count('.')
        contains_https = 1 if url.startswith('https://') else 0
        contains_login_form = 1 if 'login' in url.lower() else 0
        contains_redirect = 1 if 'redirect' in url.lower() else 0
        special_chars = len(re.findall(r'[%\-_=+/?]', url))
        path_depth = len(url.split('/')) - 3 if url else 0
        return {
            'length_domain': length_domain,
            'subdomains_count': subdomains_count,
            'contains_https': contains_https,
            'contains_login_form': contains_login_form,
            'contains_redirect': contains_redirect,
            'special_chars': special_chars,
            'path_depth': path_depth
        }
    except Exception as e:
        logging.warning(f"Erro ao extrair features de {url}: {str(e)}")
        return None

# Carregar dataset
try:
    logging.info("Carregando dataset_phishing_and_security.csv")
    # Ler CSV como texto bruto para processar linhas manualmente
    with open('dataset_phishing_and_security.csv', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Processar linhas
    data = []
    for line in lines[1:]:  # Ignorar cabeçalho
        try:
            # Dividir pela sequência de vírgulas (,,,,,,,)
            parts = line.strip().split(',,,,,,,')
            if len(parts) == 2:
                phising_url, safe_url = parts
                data.append([phising_url.strip(), safe_url.strip()])
            else:
                logging.warning(f"Linha ignorada: {line.strip()}")
        except Exception as e:
            logging.warning(f"Erro ao processar linha: {line.strip()}: {str(e)}")

    # Criar DataFrame
    df = pd.DataFrame(data, columns=['PHISING_URL', 'SAFE_URL'])
    logging.info(f"Dataset carregado com {len(df)} linhas")
except Exception as e:
    logging.error(f"Erro ao carregar CSV: {str(e)}")
    raise

# Preparar dados
features = []
labels = []
for _, row in df.iterrows():
    if pd.notna(row['PHISING_URL']):
        phishing_features = extract_features(row['PHISING_URL'])
        if phishing_features:
            features.append(phishing_features)
            labels.append(1)
    if pd.notna(row['SAFE_URL']):
        safe_features = extract_features(row['SAFE_URL'])
        if safe_features:
            features.append(safe_features)
            labels.append(0)

if not features:
    logging.error("Nenhum dado válido encontrado no dataset")
    raise ValueError("Nenhum dado válido encontrado no dataset")

X = pd.DataFrame(features)
y = pd.Series(labels)

# Verificar balanceamento
logging.info(f"Distribuição de classes: {y.value_counts()}")

# Dividir dados
try:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
except ValueError as e:
    logging.error(f"Erro ao dividir dados: {str(e)}")
    raise

# Ajustar hiperparâmetros
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5]
}
grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5, n_jobs=-1)

try:
    logging.info("Iniciando treinamento do modelo")
    grid_search.fit(X_train, y_train)
except Exception as e:
    logging.error(f"Erro durante o treinamento: {str(e)}")
    raise

# Melhor modelo
best_model = grid_search.best_estimator_

# Avaliação
y_pred = best_model.predict(X_test)
logging.info(f"Acurácia: {accuracy_score(y_test, y_pred):.4f}")
logging.info(f"Precisão: {precision_score(y_test, y_pred, pos_label=1):.4f}")
logging.info(f"Recall: {recall_score(y_test, y_pred, pos_label=1):.4f}")
logging.info(f"F1-Score: {f1_score(y_test, y_pred, pos_label=1):.4f}")

# Validação cruzada
scores = cross_val_score(best_model, X, y, cv=5)
logging.info(f"Acurácia média (CV): {scores.mean():.4f} (+/- {scores.std():.2f})")

# Salvar modelo
with open('url_classifier_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
logging.info("Modelo treinado e salvo com sucesso")