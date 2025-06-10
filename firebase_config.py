from firebase_admin import credentials, firestore, initialize_app

# Inicializar Firebase con las credenciales (ajusta la ruta según tu configuración)
cred = credentials.Certificate('path/to/your/serviceAccountKey.json')  # Reemplaza con la ruta real
initialize_app(cred)

db = firestore.client()

def save_json(data):
    try:
        # Sobrescribir el documento 'default_user' en la colección 'entreno_verano'
        db.collection('entreno_verano').document('default_user').set(data)
        print(f"Datos guardados en Firestore bajo 'default_user': {data}")
        return True
    except Exception as e:
        print(f"Error al guardar en Firestore: {str(e)}")
        return False

def get_json():
    try:
        doc = db.collection('entreno_verano').document('default_user').get()
        if doc.exists:
            return [doc.to_dict()]
        return []
    except Exception as e:
        print(f"Error al leer desde Firestore: {str(e)}")
        return []
