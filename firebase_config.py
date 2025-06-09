import os
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate({
    "type": os.environ.get('FIREBASE_TYPE'),
    "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
    "auth_uri": os.environ.get('FIREBASE_AUTH_URI'),
    "token_uri": os.environ.get('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.environ.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_X509_CERT_URL')
})
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_json(data):
    doc_id = data.get('nombre', 'default_user')  # Usa el nombre como ID único
    print(f"Datos enviados a Firestore para {doc_id}: {data}")
    db.collection('entreno_verano').document(doc_id).set(data)  # Actualiza o crea el documento
    return doc_id

def get_json():
    docs = db.collection('entreno_verano').get()
    return [doc.to_dict() for doc in docs]

__all__ = ['save_json', 'get_json']
