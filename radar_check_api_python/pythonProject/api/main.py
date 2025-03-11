# fichier: main.py
from flask import Flask
import AnalyseSuitesArithmetiques
import AnalyseSuitesArithmetiquesTirageJour
import lottery_analyzer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Enregistrer les routes de l'API 1 avec le préfixe /api1
app.register_blueprint(AnalyseSuitesArithmetiques.api, url_prefix='/AnalyseSuitesArithmetiques')

# Enregistrer les routes de l'API 2 avec le préfixe /api2
app.register_blueprint(AnalyseSuitesArithmetiquesTirageJour.api, url_prefix='/AnalyseSuitesArithmetiquesTirageJour')

# Enregistrer le nouvel analyseur avec son propre préfixe
app.register_blueprint(lottery_analyzer.api, url_prefix='/LotterySequenceAnalyzer')

if __name__ == '__main__':
    # Définir le port sur lequel les deux API seront exécutées
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)