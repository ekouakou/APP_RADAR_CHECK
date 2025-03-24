from flask import Flask
import AnalyseSuitesArithmetiques
import AnalyseSuitesArithmetiquesTirageJour
import progressions_regression_constantes
from MyLotoDataApi._AnalyseTop import api as analyse_suites_api
from MyLotoDataApi._terminaison import api as analyse_terminaison_api
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Enregistrer les routes de l'API 1 avec le préfixe /api1
app.register_blueprint(AnalyseSuitesArithmetiques.api, url_prefix='/analyse_suites_arithmetiques')

# Enregistrer les routes de l'API 2 avec le préfixe /api2
app.register_blueprint(AnalyseSuitesArithmetiquesTirageJour.api, url_prefix='/analyse_suites_arithmetiques_jour')

# Enregistrer le nouvel analyseur avec son propre préfixe
app.register_blueprint(progressions_regression_constantes.api, url_prefix='/progress_regress_constantes')

""" ---------------------------------------------------------------------------------------------------
------------------------------------- GOOD API IMPLEMENTATION -------------------------------------
--------------------------------------------------------------------------------------------------- """
# GOOD API IMPLEMENTATION
app.register_blueprint(analyse_suites_api, url_prefix='/api')  # Ajout du préfixe '/api'
app.register_blueprint(analyse_terminaison_api, url_prefix='/api')  # Ajout du préfixe '/api'

if __name__ == '__main__':
    # Définir le port sur lequel les deux API seront exécutées
    port = 5007
    app.run(host='0.0.0.0', port=port, debug=True)