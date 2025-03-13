# fichier: main.py
from flask import Flask
import AnalyseSuitesArithmetiques
import AnalyseSuitesArithmetiquesTirageJour
import progressions_regression_constantes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Enregistrer les routes de l'API 1 avec le préfixe /api1
app.register_blueprint(AnalyseSuitesArithmetiques.api, url_prefix='/analyse_suites_arithmetiques')

# Enregistrer les routes de l'API 2 avec le préfixe /api2
app.register_blueprint(AnalyseSuitesArithmetiquesTirageJour.api, url_prefix='/analyse_suites_arithmetiques_jour')

# Enregistrer le nouvel analyseur avec son propre préfixe
app.register_blueprint(progressions_regression_constantes.api, url_prefix='/progress_regress_constantes')

if __name__ == '__main__':
    # Définir le port sur lequel les deux API seront exécutées
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)