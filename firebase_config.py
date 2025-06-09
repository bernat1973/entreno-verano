from firebase_admin import firestore, initialize_app, credentials
import os

cred = credentials.Certificate("firebase-adminsdk.json") if os.path.exists("firebase-adminsdk.json") else credentials.Certificate({
    "type": os.environ.get("FIREBASE_TYPE"),
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    # ... otras claves ...
})
initialize_app(cred)
db = firestore.client()

def save_json(data):
    try:
        doc_ref = db.collection('entreno_verano').document('default_user')
        doc_ref.set(data)
        print("Datos guardados en Firestore")
    except Exception as e:
        print(f"Error al guardar en Firestore: {str(e)}")

def get_json():
    try:
        doc_ref = db.collection('entreno_verano').document('default_user').get()
        return [doc_ref.to_dict()] if doc_ref.exists else []
    except Exception as e:
        print(f"Error al obtener datos de Firestore: {str(e)}")
        return []
