# fichier: main.py
from flask import Flask
import AnanlyseSuite1
import AnanlyseSuite2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Enregistrer les routes de l'API 1 avec le préfixe /api1
app.register_blueprint(AnanlyseSuite1.bp, url_prefix='/api1')

# Enregistrer les routes de l'API 2 avec le préfixe /api2
app.register_blueprint(AnanlyseSuite2.bp, url_prefix='/api2')

if __name__ == '__main__':
    # Définir le port sur lequel les deux API seront exécutées
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)