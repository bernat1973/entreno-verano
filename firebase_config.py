from firebase_admin import firestore, initialize_app, credentials
import os

try:
    if os.path.exists("firebase-adminsdk.json"):
        cred = credentials.Certificate("firebase-adminsdk.json")
    else:
        required_env = ["FIREBASE_TYPE", "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID", "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL", "FIREBASE_CLIENT_ID", "FIREBASE_AUTH_URI", "FIREBASE_TOKEN_URI", "FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "FIREBASE_CLIENT_X509_CERT_URL"]
        missing_env = [var for var in required_env if not os.environ.get(var)]
        if missing_env:
            raise ValueError(f"Variables de entorno faltantes: {missing_env}")
        cred = credentials.Certificate({
            "type": os.environ.get("FIREBASE_TYPE"),
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
            "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
        })
    initialize_app(cred)
    db = firestore.client()
    print("Firebase inicializado correctamente")
except Exception as e:
    print(f"Error al inicializar Firebase: {str(e)}")
    raise

def save_json(data):
    try:
        if not data or not isinstance(data, dict):
            print("Error: Datos inválidos para guardar en Firestore")
            return False
        doc_ref = db.collection('entreno_verano').document('default_user')
        doc_ref.set(data)
        print(f"Datos guardados en Firestore: {data}")
        return True
    except Exception as e:
        print(f"Error al guardar en Firestore: {str(e)}")
        return False

def get_json():
    try:
        doc_ref = db.collection('entreno_verano').document('default_user').get()
        return [doc_ref.to_dict()] if doc_ref.exists else []
    except Exception as e:
        print(f"Error al obtener datos de Firestore: {str(e)}")
        return []

