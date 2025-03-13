import csv
import re
from datetime import datetime
import math


class AnalyseurTirage:
    def __init__(self, fichier_csv):
        self.fichier_csv = fichier_csv
        self.donnees = []
        self.resultats = []
        self.pagination_active = False
        self.items_par_page = 10
        self.page_courante = 1

    def charger_donnees(self):
        """Charge les données du fichier CSV"""
        try:
            with open(self.fichier_csv, 'r', encoding='utf-8') as fichier:
                lecteur = csv.reader(fichier, delimiter=';')
                entetes = next(lecteur)  # Lire les en-têtes

                # Détecter les indices des colonnes importantes
                self.index_date = entetes.index('Date') if 'Date' in entetes else 0
                self.index_type = entetes.index('Type de Tirage') if 'Type de Tirage' in entetes else 3

                # Trouver les indices des colonnes de numéros
                self.indices_num = [i for i, col in enumerate(entetes) if re.match(r'Num\d+', col)]
                self.indices_machine = [i for i, col in enumerate(entetes) if re.match(r'Machine\d+', col)]

                # Charger toutes les lignes
                for ligne in lecteur:
                    if ligne:  # Ignorer les lignes vides
                        self.donnees.append(ligne)

                print(f"Fichier chargé avec succès: {len(self.donnees)} lignes trouvées.")
        except FileNotFoundError:
            print(f"Erreur: Le fichier {self.fichier_csv} n'a pas été trouvé.")
            return False
        except Exception as e:
            print(f"Erreur lors du chargement du fichier: {e}")
            return False
        return True

    def analyser(self, params=None):
        """Analyse les tirages selon les paramètres spécifiés"""
        if not self.donnees:
            print("Aucune donnée à analyser. Veuillez d'abord charger le fichier.")
            return []

        # Paramètres par défaut
        params_defaut = {
            'dates': [],  # Liste de dates spécifiques à analyser
            'date_debut': None,  # Date de début pour filtrer les résultats
            'date_fin': None,  # Date de fin pour filtrer les résultats
            'types_suites': ["arithmetique", "geometrique", "diff_croissante", "diff_decroissante"],
            'ordre': "croissant",  # "croissant" ou "decroissant"
            'min_elements': 3,  # Nombre minimum d'éléments pour une suite valide
            'forcer_min': True,  # Forcer le nombre minimum d'éléments
            'verifier_completion': False,  # Vérifier si tous les nombres de 1 à 90 sont présents
            'respecter_position': False,  # Respecter l'ordre des colonnes
            'source_numeros': "tous",  # "num", "machine" ou "tous"
            'ordre_lecture': "normal",  # "normal" ou "inverse"
            'types_tirage': [],  # Filtrer par type de tirage
            'sens_analyse': "horizontal",  # "horizontal", "vertical" ou "les_deux"
            'pagination': False,  # Activer/désactiver la pagination
            'items_par_page': 10,  # Nombre d'éléments par page
            'page': 1  # Page courante
        }

        # Mettre à jour les paramètres par défaut avec ceux fournis
        if params:
            for cle, valeur in params.items():
                if cle in params_defaut:
                    params_defaut[cle] = valeur

        # Appliquer les paramètres
        self.pagination_active = params_defaut['pagination']
        self.items_par_page = params_defaut['items_par_page']
        self.page_courante = params_defaut['page']

        # Filtrer les données selon les paramètres
        donnees_filtrees = self.filtrer_donnees(params_defaut)

        # Analyser les suites selon le sens d'analyse
        self.resultats = []

        if params_defaut['sens_analyse'] in ["horizontal", "les_deux"]:
            self.analyser_horizontal(donnees_filtrees, params_defaut)

        if params_defaut['sens_analyse'] in ["vertical", "les_deux"]:
            self.analyser_vertical(donnees_filtrees, params_defaut)

        # Appliquer la pagination si nécessaire
        if self.pagination_active:
            debut = (self.page_courante - 1) * self.items_par_page
            fin = debut + self.items_par_page
            resultats_pages = self.resultats[debut:fin]
            return {
                'resultats': resultats_pages,
                'total': len(self.resultats),
                'pages': math.ceil(len(self.resultats) / self.items_par_page),
                'page_courante': self.page_courante
            }
        else:
            return self.resultats

    def filtrer_donnees(self, params):
        """Filtre les données selon les paramètres"""
        donnees_filtrees = self.donnees.copy()

        # Filtrer par dates spécifiques
        if params['dates']:
            donnees_filtrees = [ligne for ligne in donnees_filtrees
                                if ligne[self.index_date] in params['dates']]

        # Filtrer par plage de dates (date_debut et date_fin)
        if 'date_debut' in params and params['date_debut'] and 'date_fin' in params and params['date_fin']:
            try:
                date_debut = datetime.strptime(params['date_debut'], '%d/%m/%Y')
                date_fin = datetime.strptime(params['date_fin'], '%d/%m/%Y')

                donnees_filtrees = [ligne for ligne in donnees_filtrees
                                    if self.est_dans_plage_date(ligne[self.index_date], date_debut, date_fin)]
            except ValueError as e:
                print(f"Erreur de format de date: {e}")

        # Filtrer par type de tirage
        if params['types_tirage']:
            donnees_filtrees = [ligne for ligne in donnees_filtrees
                                if ligne[self.index_type] in params['types_tirage']]

        # Inverser l'ordre de lecture si nécessaire
        if params['ordre_lecture'] == "inverse":
            donnees_filtrees.reverse()

        return donnees_filtrees

    def est_dans_plage_date(self, date_str, date_debut, date_fin):
        """Vérifie si une date est dans la plage spécifiée"""
        try:
            # Convertir la chaîne de date en objet datetime
            date = datetime.strptime(date_str, '%d/%m/%Y')
            # Vérifier si la date est dans la plage
            return date_debut <= date <= date_fin
        except ValueError:
            # En cas d'erreur de format, retourner False
            return False

    def identifier_suites(self, numeros, type_suite, params):
        """Identifie les suites selon le type spécifié"""
        suites_trouvees = []

        if len(numeros) < params['min_elements']:
            return []

        if type_suite == "arithmetique":
            suites_trouvees.extend(self.trouver_suites_arithmetiques(numeros, params))
        elif type_suite == "geometrique":
            suites_trouvees.extend(self.trouver_suites_geometriques(numeros, params))
        elif type_suite == "diff_croissante":
            suites_trouvees.extend(self.trouver_suites_diff_variables(numeros, "croissante", params))
        elif type_suite == "diff_decroissante":
            suites_trouvees.extend(self.trouver_suites_diff_variables(numeros, "decroissante", params))

        return suites_trouvees

    def trouver_suites_arithmetiques(self, numeros, params):
        """Trouve les suites arithmétiques dans une liste de nombres"""
        suites = []
        n = len(numeros)

        for i in range(n - 1):
            for j in range(i + 1, n):
                raison = numeros[j] - numeros[i]
                if raison == 0:
                    continue

                suite = [numeros[i], numeros[j]]
                raisons = [raison]
                prochain = numeros[j] + raison

                for k in range(j + 1, n):
                    if numeros[k] == prochain:
                        suite.append(numeros[k])
                        raisons.append(raison)
                        prochain += raison

                if len(suite) >= params['min_elements'] or not params['forcer_min']:
                    suites.append((suite, raisons))

        return suites

    def trouver_suites_geometriques(self, numeros, params):
        """Trouve les suites géométriques dans une liste de nombres"""
        suites = []
        n = len(numeros)

        for i in range(n - 1):
            if numeros[i] == 0:
                continue

            for j in range(i + 1, n):
                if numeros[j] == 0:
                    continue

                raison = numeros[j] / numeros[i]
                if raison == 1:
                    continue

                suite = [numeros[i], numeros[j]]
                raisons = [raison]
                prochain = numeros[j] * raison

                for k in range(j + 1, n):
                    # Utiliser une tolérance pour les erreurs d'arrondi
                    if abs(numeros[k] - prochain) < 0.001:
                        suite.append(numeros[k])
                        raisons.append(raison)
                        prochain *= raison

                if len(suite) >= params['min_elements'] or not params['forcer_min']:
                    suites.append((suite, raisons))

        return suites

    def trouver_suites_diff_variables(self, numeros, direction, params):
        """Trouve les suites à différences variables"""
        suites = []
        n = len(numeros)

        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                diff1 = numeros[j] - numeros[i]

                for k in range(j + 1, n):
                    diff2 = numeros[k] - numeros[j]

                    # Vérifier si les différences sont croissantes ou décroissantes
                    if (direction == "croissante" and diff2 > diff1) or \
                            (direction == "decroissante" and diff2 < diff1):

                        suite = [numeros[i], numeros[j], numeros[k]]
                        raisons = [diff1, diff2]
                        diff_precedente = diff2

                        # Rechercher des numéros qui continuent la suite
                        prochain_attendu = numeros[k]
                        for l in range(k + 1, n):
                            diff_potentielle = numeros[l] - prochain_attendu

                            if (direction == "croissante" and diff_potentielle > diff_precedente) or \
                                    (direction == "decroissante" and diff_potentielle < diff_precedente):
                                suite.append(numeros[l])
                                raisons.append(diff_potentielle)
                                prochain_attendu = numeros[l]
                                diff_precedente = diff_potentielle

                        if len(suite) >= params['min_elements'] or not params['forcer_min']:
                            suites.append((suite, raisons))

        return suites

    def verifier_completion(self, suite):
        """Vérifie si une suite est complète en identifiant tous les nombres manquants de la suite"""
        # Si la suite est vide ou n'a qu'un élément, elle ne peut pas être complète
        if len(suite) <= 1:
            return []

        # Pour les suites arithmétiques
        nombres_manquants = []

        # Déterminer la raison de la suite
        if len(suite) >= 2:
            # Calculer la raison (différence entre termes consécutifs)
            raison = suite[1] - suite[0]

            # Vérifier si tous les éléments de la suite ont la même raison
            raisons_constantes = True
            for i in range(1, len(suite) - 1):
                if suite[i + 1] - suite[i] != raison:
                    raisons_constantes = False
                    break

            # Si la raison est constante, on peut identifier les nombres manquants
            if raisons_constantes:
                # Déterminer si la suite est croissante ou décroissante
                est_croissante = raison > 0

                # Trouver le début et la fin de la suite actuelle
                debut_actuel = min(suite)
                fin_actuelle = max(suite)

                # Calculer combien de termes il peut y avoir avant le premier terme de la suite
                termes_avant = []
                terme_potentiel = debut_actuel - raison
                # Continuer tant que les termes sont positifs (ou respectent d'autres contraintes si nécessaire)
                while terme_potentiel > 0:  # Condition pour les nombres positifs
                    termes_avant.append(terme_potentiel)
                    terme_potentiel -= raison

                # Calculer combien de termes il peut y avoir après le dernier terme de la suite
                termes_apres = []
                terme_potentiel = fin_actuelle + raison
                # On peut ajouter d'autres conditions pour limiter l'étendue (par exemple, terme_potentiel <= 90 pour le loto)
                # Pour cet exemple, on se limite à quelques termes après
                for _ in range(5):  # Limiter à 5 termes après pour éviter une liste infinie
                    termes_apres.append(terme_potentiel)
                    terme_potentiel += raison

                # Générer la liste complète des nombres qui devraient être dans la suite
                nombres_attendus = []
                # Ajouter les termes avant dans l'ordre inverse (pour respecter l'ordre croissant/décroissant)
                nombres_attendus.extend(reversed(termes_avant))

                # Générer tous les nombres entre le début et la fin actuels
                current = debut_actuel
                while (est_croissante and current <= fin_actuelle) or (not est_croissante and current >= fin_actuelle):
                    nombres_attendus.append(current)
                    current += raison

                # Ajouter les termes après
                nombres_attendus.extend(termes_apres)

                # Identifier les nombres manquants (tous ceux qui sont attendus mais pas dans la suite)
                nombres_manquants = [n for n in nombres_attendus if n not in suite]

        return nombres_manquants

    def verifier_completion__(self, suite):
        """Vérifie si une suite est complète en identifiant les nombres manquants de la suite"""
        # Si la suite est vide ou n'a qu'un élément, elle ne peut pas être complète
        if len(suite) <= 1:
            return []

        # Pour les suites arithmétiques
        nombres_manquants = []

        # Déterminer la raison de la suite
        if len(suite) >= 2:
            # Vérifier si tous les éléments de la suite ont la même raison
            raisons_constantes = True
            raison = suite[1] - suite[0]

            for i in range(1, len(suite) - 1):
                if suite[i + 1] - suite[i] != raison:
                    raisons_constantes = False
                    break

            # Si la raison est constante, on peut identifier les nombres manquants
            if raisons_constantes:
                # Déterminer le sens de la suite (croissant ou décroissant)
                est_croissante = raison > 0

                # Trouver le début et la fin de la suite complète
                debut = min(suite)
                fin = max(suite)

                # Générer la liste complète des nombres qui devraient être dans la suite
                nombres_attendus = []
                current = debut

                while (est_croissante and current <= fin) or (not est_croissante and current >= fin):
                    nombres_attendus.append(current)
                    current += raison

                # Identifier les nombres manquants
                nombres_manquants = [n for n in nombres_attendus if n not in suite]

                # Vérifier également s'il y a des termes qui précèdent ou suivent la suite
                # Calculer le terme qui précède le plus petit terme
                terme_precedent = min(suite) - raison
                # Pour une suite croissante, vérifier si le terme précédent est positif
                # Pour une suite décroissante, vérifier si le terme suivant est positif
                if est_croissante:
                    if terme_precedent > 0:  # Si nous sommes dans le domaine des nombres positifs
                        nombres_manquants.append(terme_precedent)
                else:  # Suite décroissante
                    terme_suivant = max(suite) - raison  # Pour une suite décroissante, le terme suivant est plus petit
                    if terme_suivant > 0:  # Si nous sommes dans le domaine des nombres positifs
                        nombres_manquants.append(terme_suivant)

        return nombres_manquants

    def extraire_numeros(self, ligne, params):
        """Extrait les numéros d'une ligne selon les paramètres"""
        numeros = []
        numeros_info = []  # Liste avec les infos de colonne

        if params['source_numeros'] in ["num", "tous"]:
            for i, idx in enumerate(self.indices_num):
                if idx < len(ligne) and ligne[idx]:
                    try:
                        num = int(ligne[idx])
                        numeros.append(num)
                        numeros_info.append((num, f"Num{i + 1}"))
                    except ValueError:
                        pass

        if params['source_numeros'] in ["machine", "tous"]:
            for i, idx in enumerate(self.indices_machine):
                if idx < len(ligne) and ligne[idx]:
                    try:
                        num = int(ligne[idx])
                        numeros.append(num)
                        numeros_info.append((num, f"Machine{i + 1}"))
                    except ValueError:
                        pass

        # Trier les numéros si on ne respecte pas la position
        if not params['respecter_position']:
            # Tri avec conservation de l'information de position
            numeros_info.sort(key=lambda x: x[0], reverse=(params['ordre'] == "decroissant"))
            numeros = [x[0] for x in numeros_info]
        else:
            numeros_info = [(num, col) for num, col in numeros_info]

        return numeros, numeros_info

    def analyser_horizontal(self, donnees, params):
        """Analyse les suites horizontalement (dans chaque tirage)"""
        for ligne in donnees:
            numeros, numeros_info = self.extraire_numeros(ligne, params)

            # Analyser selon les types de suites demandés
            for type_suite in params['types_suites']:
                suites_trouvees = self.identifier_suites(numeros, type_suite, params)

                for suite, raisons in suites_trouvees:
                    if suite and len(suite) >= params['min_elements']:
                        # Récupérer les informations de colonne pour chaque numéro de la suite
                        colonnes_suite = []
                        for num in suite:
                            for n_info in numeros_info:
                                if n_info[0] == num:
                                    colonnes_suite.append(n_info[1])
                                    break

                        resultat = {
                            'date': ligne[self.index_date],
                            'type_tirage': ligne[self.index_type],
                            'type_suite': type_suite,
                            'suite': suite,
                            'colonnes': colonnes_suite,  # Ajout des colonnes
                            'raisons': raisons,
                            'sens': 'horizontal'
                        }

                        # Vérifier la complétion si demandé
                        if params['verifier_completion']:
                            manquants = self.verifier_completion(suite)
                            resultat['complete'] = len(manquants) == 0
                            resultat['manquants'] = manquants

                        self.resultats.append(resultat)

    def analyser_vertical(self, donnees, params):
        """Analyse les suites verticalement (à travers différents tirages)"""
        # Organiser les numéros par position
        numeros_par_position = {}

        for pos in range(max(len(self.indices_num), len(self.indices_machine))):
            numeros_par_position[pos] = []

            for ligne in donnees:
                if params['source_numeros'] in ["num", "tous"] and pos < len(self.indices_num):
                    idx = self.indices_num[pos]
                    if idx < len(ligne) and ligne[idx]:
                        try:
                            numeros_par_position[pos].append(
                                (int(ligne[idx]), ligne[self.index_date], ligne[self.index_type], f"Num{pos + 1}"))
                        except ValueError:
                            pass

                if params['source_numeros'] in ["machine", "tous"] and pos < len(self.indices_machine):
                    idx = self.indices_machine[pos]
                    if idx < len(ligne) and ligne[idx]:
                        try:
                            numeros_par_position[pos].append(
                                (int(ligne[idx]), ligne[self.index_date], ligne[self.index_type], f"Machine{pos + 1}"))
                        except ValueError:
                            pass

        # Analyser chaque position
        for pos, numeros_info in numeros_par_position.items():
            if not params['respecter_position']:
                numeros_info.sort(key=lambda x: x[0], reverse=(params['ordre'] == "decroissant"))

            numeros = [n[0] for n in numeros_info]

            # Analyser selon les types de suites demandés
            for type_suite in params['types_suites']:
                suites_trouvees = self.identifier_suites(numeros, type_suite, params)

                for suite, raisons in suites_trouvees:
                    if suite and len(suite) >= params['min_elements']:
                        # Trouver les informations associées à chaque numéro de la suite
                        infos_suite = []
                        colonnes_suite = []
                        for num in suite:
                            for n_info in numeros_info:
                                if n_info[0] == num:
                                    infos_suite.append((n_info[0], n_info[1], n_info[2], n_info[3]))
                                    colonnes_suite.append(n_info[3])
                                    break

                        resultat = {
                            'position': pos + 1,
                            'type_suite': type_suite,
                            'suite': suite,
                            'colonnes': colonnes_suite,  # Ajout des colonnes
                            'raisons': raisons,
                            'infos': infos_suite,
                            'sens': 'vertical'
                        }

                        # Vérifier la complétion si demandé
                        if params['verifier_completion']:
                            manquants = self.verifier_completion(suite)
                            resultat['complete'] = len(manquants) == 0
                            resultat['manquants'] = manquants

                        self.resultats.append(resultat)

    def afficher_resultats(self):
        """Affiche les résultats de l'analyse"""
        if not self.resultats:
            print("Aucun résultat trouvé.")
            return

        print(f"\n=== RÉSULTATS DE L'ANALYSE ({len(self.resultats)} suites trouvées) ===\n")

        for i, res in enumerate(self.resultats, 1):
            print(f"Résultat #{i}:")

            if res['sens'] == 'horizontal':
                print(f"Date: {res['date']}")
                print(f"Type de tirage: {res['type_tirage']}")
            else:  # vertical
                print(f"Position: {res['position']}")
                print("Infos: ", end="")
                for idx, info in enumerate(res['infos']):
                    if len(info) >= 4:  # Vérifier que nous avons bien 4 éléments
                        print(f"{info[0]} ({info[1]}, {info[2]}, {info[3]})", end=", ")
                    else:
                        print(f"{info[0]} ({info[1]}, {info[2]})", end=", ")
                print()

            print(f"Type de suite: {res['type_suite']}")
            print(f"Suite: {res['suite']}")

            # Afficher les colonnes correspondantes
            print("Colonnes: ", end="")
            for col in res['colonnes']:
                print(f"{col}", end=", ")
            print()

            print(f"Raisons: {res['raisons']}")

            if 'complete' in res:
                print(f"Complète: {'Oui' if res['complete'] else 'Non'}")
                if not res['complete']:
                    print(f"Nombres manquants: {res['manquants']}")

            print()


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration de l'analyse
    fichier = "/Users/imac/Documents/NKM-TECHNOLOGY/APP_RADAR_CHECK/radar_check_api_python/pythonProject/api/uploads/formatted_lottery_results.csv"  # Utilisez le nom exact de votre fichier

    # Initialiser l'analyseur
    analyseur = AnalyseurTirage(fichier)

    # Charger les données
    if analyseur.charger_donnees():
        # Définir les paramètres d'analyse
        parametres = {
            #'dates': ["05/10/2020", "06/10/2020", "07/10/2020", "08/10/2020"],  # Dates spécifiques
            'types_suites': ["arithmetique", "geometrique"],
            'date_debut': "01/01/2020",
            'date_fin': "31/12/2020",
            'ordre': "decroissant",  # decroissant #croissant
            'min_elements': 4,
            'forcer_min': True,
            'verifier_completion': True,
            'respecter_position': False,
            'source_numeros': "tous",  # "num", "machine" ou "tous"
            'ordre_lecture': "normal",
            'types_tirage': ["Reveil", "Sika"],  # Filtrer par type de tirage
            'sens_analyse': "les_deux",  # "horizontal", "vertical" ou "les_deux"
            'pagination': False,
            'items_par_page': 50,
            'page': 2
        }

        # Effectuer l'analyse
        resultats = analyseur.analyser(parametres)

        # Afficher les résultats
        if isinstance(resultats, dict):  # Résultats paginés
            print(f"Page {resultats['page_courante']}/{resultats['pages']} - "
                  f"Affichage de {len(resultats['resultats'])} sur {resultats['total']} résultats")

            analyseur.resultats = resultats['resultats']
            analyseur.afficher_resultats()
        else:  # Tous les résultats
            analyseur.afficher_resultats()
