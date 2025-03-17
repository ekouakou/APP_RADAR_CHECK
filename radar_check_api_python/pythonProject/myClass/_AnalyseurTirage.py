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

    def trouver_suites_harshad(self, numeros, params):
        """
        Trouve les nombres de Harshad (ou Niven) dans une liste de nombres.
        Un nombre de Harshad est divisible par la somme de ses chiffres.
        """
        harshad = [num for num in numeros if num > 0 and num % sum(int(ch) for ch in str(num)) == 0]
        harshad.sort()

        if len(harshad) < params.get('min_elements', 0):
            return []

        raisons = [harshad[i + 1] - harshad[i] for i in range(len(harshad) - 1)] if len(harshad) > 1 else []
        return [(harshad, raisons)]

    def trouver_suites_octogonaux(self, numeros, params):
        """Trouve les nombres octogonaux dans la liste."""
        octogonaux_ref = [n * (3 * n - 2) for n in range(1, 10) if n * (3 * n - 2) <= 90]
        octogonaux = sorted([num for num in numeros if num in octogonaux_ref])

        if len(octogonaux) < params.get('min_elements', 0):
            return []

        raisons = [octogonaux[i + 1] - octogonaux[i] for i in range(len(octogonaux) - 1)] if len(octogonaux) > 1 else []
        return [(octogonaux, raisons)]

    def trouver_suites_pentagonaux(self, numeros, params):
        """Trouve les nombres pentagonaux dans la liste."""
        pentagonaux_ref = [n * (3 * n - 1) // 2 for n in range(1, 10) if n * (3 * n - 1) // 2 <= 90]
        pentagonaux = sorted([num for num in numeros if num in pentagonaux_ref])

        if len(pentagonaux) < params.get('min_elements', 0):
            return []

        raisons = [pentagonaux[i + 1] - pentagonaux[i] for i in range(len(pentagonaux) - 1)] if len(
            pentagonaux) > 1 else []
        return [(pentagonaux, raisons)]

    def trouver_suites_thabit(self, numeros, params):
        """Trouve les nombres de Thabit dans la liste."""
        thabit_ref = [3 * (2 ** n) - 1 for n in range(7) if 3 * (2 ** n) - 1 <= 90]
        thabit = sorted([num for num in numeros if num in thabit_ref])

        if len(thabit) < params.get('min_elements', 0):
            return []

        raisons = [thabit[i + 1] - thabit[i] for i in range(len(thabit) - 1)] if len(thabit) > 1 else []
        return [(thabit, raisons)]

    def trouver_suites_chanceux(self, numeros, params):
        """Trouve les nombres chanceux dans la liste."""
        nombres = list(range(1, 91, 2))
        i = 1

        while i < len(nombres):
            if i >= len(nombres):
                break
            compteur = nombres[i]
            del nombres[compteur - 1::compteur]
            i += 1

        chanceux = sorted([num for num in numeros if num in nombres])

        if len(chanceux) < params.get('min_elements', 0):
            return []

        raisons = [chanceux[i + 1] - chanceux[i] for i in range(len(chanceux) - 1)] if len(chanceux) > 1 else []
        return [(chanceux, raisons)]

    def trouver_suites_keith(self, numeros, params):
        """Trouve les nombres de Keith dans la liste."""
        keith_ref = {14, 19, 28, 47, 61, 75}
        keith = sorted([num for num in numeros if num in keith_ref])

        if len(keith) < params.get('min_elements', 0):
            return []

        raisons = [keith[i + 1] - keith[i] for i in range(len(keith) - 1)] if len(keith) > 1 else []
        return [(keith, raisons)]

    def trouver_suites_catalan(self, numeros, params):
        """Trouve les nombres de Catalan dans la liste."""
        catalan_ref = []
        n, c_n = 0, 1

        while c_n <= 90:
            catalan_ref.append(c_n)
            c_n = c_n * (4 * n + 2) // (n + 2)
            n += 1

        catalan = sorted([num for num in numeros if num in catalan_ref])

        if len(catalan) < params.get('min_elements', 0):
            return []

        raisons = [catalan[i + 1] - catalan[i] for i in range(len(catalan) - 1)] if len(catalan) > 1 else []
        return [(catalan, raisons)]


    def trouver_suites_polygonaux(self, numeros, params):
        """
        Trouve les nombres polygonaux généralisés dans une liste de nombres.
        Le n-ième nombre s-gonal est donné par: P(s,n) = (s-2)*n*(n-1)/2 + n
        """
        resultats = []
        max_val = max(numeros) if numeros else 90  # Déterminer la valeur maximale utile

        for s in range(3, 10):  # Tester des polygones de 3 à 9 côtés
            polygonaux = []
            polygonaux_ref = set()  # Utilisation d'un ensemble pour une recherche rapide

            # Générer les nombres s-gonaux jusqu'à la valeur max trouvée
            n = 1
            while True:
                p_n = (s - 2) * n * (n - 1) // 2 + n
                if p_n > max_val:
                    break
                polygonaux_ref.add(p_n)
                n += 1

            # Vérifier quels nombres de la liste sont polygonaux de type `s`
            polygonaux = sorted([num for num in numeros if num in polygonaux_ref])

            # Vérifier que la suite contient suffisamment d'éléments
            if len(polygonaux) >= params.get('min_elements', 3):  # Valeur par défaut 3
                raisons = [polygonaux[i + 1] - polygonaux[i] for i in range(len(polygonaux) - 1)]
                resultats.append((polygonaux, raisons))

        return resultats

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
            'types_suites': [
                "arithmetique", "geometrique", "diff_croissante", "diff_decroissante",
                "premiers", "carres_parfaits", "triangulaires", "fibonacci",
                "pairs", "impairs", "multiples_3", "multiples_7"
            ],
            'ordre': "croissant",  # "croissant" ou "decroissant"
            'min_elements': 3,  # Nombre minimum d'éléments pour une suite valide
            'forcer_min': True,  # Forcer le nombre minimum d'éléments
            'verifier_completion': False,  # Vérifier si tous les nombres de 1 à 90 sont présents
            'respecter_position': False,  # Respecter l'ordre des colonnes
            'source_numeros': "tous",  # "num", "machine" ou "tous"
            'ordre_lecture': "normal",  # "normal" ou "inverse"
            'types_tirage': [],  # Filtrer par type de tirage
            'sens_analyse': "horizontal",  # "horizontal", "vertical", "les_deux" ou "bidirectionnel"
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

        if params_defaut['sens_analyse'] == "horizontal":
            self.analyser_horizontal(donnees_filtrees, params_defaut)
        elif params_defaut['sens_analyse'] == "vertical":
            self.analyser_vertical(donnees_filtrees, params_defaut)
        elif params_defaut['sens_analyse'] == "les_deux" or params_defaut['sens_analyse'] == "bidirectionnel":
            # Utiliser la nouvelle fonction qui combine les deux analyses
            self.analyser_les_deux(donnees_filtrees, params_defaut)

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
        elif type_suite == "premiers":
            suites_trouvees.extend(self.trouver_suites_nombres_premiers(numeros, params))
            # Suites existantes
        elif type_suite == "carres_parfaits":
            suites_trouvees.extend(self.trouver_suites_carres_parfaits(numeros, params))
        elif type_suite == "triangulaires":
            suites_trouvees.extend(self.trouver_suites_triangulaires(numeros, params))
        elif type_suite == "fibonacci":
            suites_trouvees.extend(self.trouver_suites_fibonacci(numeros, params))
            # Nouvelles suites ajoutées
        elif type_suite == "harshad":
            suites_trouvees.extend(self.trouver_suites_harshad(numeros, params))
        elif type_suite == "octogonaux":
            suites_trouvees.extend(self.trouver_suites_octogonaux(numeros, params))
        elif type_suite == "pentagonaux":
            suites_trouvees.extend(self.trouver_suites_pentagonaux(numeros, params))
        elif type_suite == "thabit":
            suites_trouvees.extend(self.trouver_suites_thabit(numeros, params))
        elif type_suite == "chanceux":
            suites_trouvees.extend(self.trouver_suites_chanceux(numeros, params))
        elif type_suite == "keith":
            suites_trouvees.extend(self.trouver_suites_keith(numeros, params))
        elif type_suite == "catalan":
            suites_trouvees.extend(self.trouver_suites_catalan(numeros, params))
        elif type_suite == "polygonaux":
            suites_trouvees.extend(self.trouver_suites_polygonaux(numeros, params))
        # Suites basées sur des critères spécifiques
        elif type_suite == "pairs":
            suites_trouvees.extend(self.trouver_suites_specifiques(numeros, "pairs", params))
        elif type_suite == "impairs":
            suites_trouvees.extend(self.trouver_suites_specifiques(numeros, "impairs", params))
        elif type_suite.startswith("multiples_"):
            suites_trouvees.extend(self.trouver_suites_specifiques(numeros, type_suite, params))

        return suites_trouvees

    def trouver_suites_carres_parfaits(self, numeros, params):
        """Trouve les suites de carrés parfaits dans une liste de nombres"""
        # Identifier les carrés parfaits dans la liste des numéros
        carres_parfaits = []
        for num in numeros:
            # Vérifier si le nombre est un carré parfait
            racine = int(num ** 0.5)
            if racine * racine == num:
                carres_parfaits.append(num)

        # Trier les carrés parfaits
        carres_parfaits.sort()

        # Si on n'a pas assez de carrés parfaits, retourner une liste vide
        if len(carres_parfaits) < params['min_elements']:
            return []

        # Construire la suite et les raisons (différences entre les nombres consécutifs)
        suite = carres_parfaits
        raisons = [suite[i + 1] - suite[i] for i in range(len(suite) - 1)]

        return [(suite, raisons)]

    def trouver_suites_triangulaires(self, numeros, params):
        """Trouve les suites de nombres triangulaires dans une liste de nombres"""
        # Un nombre triangulaire n est de la forme n(n+1)/2
        # On peut vérifier si un nombre est triangulaire avec la formule inverse:
        # n = (-1 + sqrt(1 + 8*N))/2 où N est le nombre à tester

        triangulaires = []
        for num in numeros:
            # Formule pour vérifier si un nombre est triangulaire
            n = (-1 + (1 + 8 * num) ** 0.5) / 2
            if n.is_integer():
                triangulaires.append(num)

        # Trier les nombres triangulaires
        triangulaires.sort()

        # Si on n'a pas assez de nombres triangulaires, retourner une liste vide
        if len(triangulaires) < params['min_elements']:
            return []

        # Construire la suite et les raisons (différences entre les nombres consécutifs)
        suite = triangulaires
        raisons = [suite[i + 1] - suite[i] for i in range(len(suite) - 1)]

        return [(suite, raisons)]

    def generer_fibonacci(self, max_value=90):
        """Génère la séquence de Fibonacci jusqu'à la valeur spécifiée"""
        fib = [1, 1]
        while fib[-1] + fib[-2] <= max_value:
            fib.append(fib[-1] + fib[-2])
        return fib

    def trouver_suites_fibonacci(self, numeros, params):
        """Trouve les suites de Fibonacci dans une liste de nombres"""
        # Générer la suite de Fibonacci jusqu'à 90 (limite de loterie standard)
        fibonacci = self.generer_fibonacci(90)

        # Identifier les nombres de Fibonacci dans la liste
        nums_fibonacci = [num for num in numeros if num in fibonacci]

        # Éliminer les doublons et trier
        nums_fibonacci = sorted(list(set(nums_fibonacci)))

        # Si on n'a pas assez de nombres de Fibonacci, retourner une liste vide
        if len(nums_fibonacci) < params['min_elements']:
            return []

        # Construire la suite et les raisons (différences entre les nombres consécutifs)
        suite = nums_fibonacci
        raisons = [suite[i + 1] - suite[i] for i in range(len(suite) - 1)]

        return [(suite, raisons)]

    def trouver_suites_specifiques(self, numeros, critere, params):
        """
        Trouve les suites basées sur des critères spécifiques:
        - pairs: nombres pairs
        - impairs: nombres impairs
        - multiples_X: multiples de X (où X est un entier)
        """
        numeros_filtres = []

        if critere == "pairs":
            numeros_filtres = [num for num in numeros if num % 2 == 0]
        elif critere == "impairs":
            numeros_filtres = [num for num in numeros if num % 2 != 0]
        elif critere.startswith("multiples_"):
            try:
                diviseur = int(critere.split("_")[1])
                numeros_filtres = [num for num in numeros if num % diviseur == 0]
            except (IndexError, ValueError):
                return []

        # Trier les nombres filtrés
        numeros_filtres.sort()

        # Si on n'a pas assez de nombres selon le critère, retourner une liste vide
        if len(numeros_filtres) < params['min_elements']:
            return []

        # Construire la suite et les raisons (différences entre les nombres consécutifs)
        suite = numeros_filtres
        raisons = [suite[i + 1] - suite[i] for i in range(len(suite) - 1)]

        return [(suite, raisons)]

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

    def trouver_suites_diff_variables___(self, numeros, direction, params):
        """
        Trouve les suites à différences variables qui suivent une progression logique.

        Args:
            numeros (list): Liste de nombres à analyser
            direction (str): "croissante" ou "decroissante" pour la progression des différences
            params (dict): Paramètres de configuration avec 'min_elements' et 'forcer_min'

        Returns:
            list: Liste de tuples (suite, raisons) où suite est une liste de nombres et
                  raisons est la liste des différences entre les nombres consécutifs
        """
        suites = []
        n = len(numeros)

        # Vérifier qu'il y a suffisamment de nombres pour former une suite
        if n < 3:
            return suites

        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                diff1 = numeros[j] - numeros[i]

                for k in range(j + 1, n):
                    diff2 = numeros[k] - numeros[j]

                    # Vérifier si les différences suivent la progression demandée
                    if (direction == "croissante" and diff2 > diff1) or \
                            (direction == "decroissante" and diff2 < diff1):

                        # Commencer une nouvelle suite potentielle
                        suite = [numeros[i], numeros[j], numeros[k]]
                        raisons = [diff1, diff2]
                        dernier_nombre = numeros[k]
                        diff_precedente = diff2

                        # Rechercher des nombres qui continuent la suite
                        for l in range(k + 1, n):
                            diff_courante = numeros[l] - dernier_nombre

                            # Vérifier si la différence respecte la progression
                            if (direction == "croissante" and diff_courante > diff_precedente) or \
                                    (direction == "decroissante" and diff_courante < diff_precedente):
                                suite.append(numeros[l])
                                raisons.append(diff_courante)
                                dernier_nombre = numeros[l]
                                diff_precedente = diff_courante

                        # Ajouter la suite si elle respecte les conditions minimales
                        if len(suite) >= params['min_elements'] or not params['forcer_min']:
                            suites.append((suite, raisons))

        return suites

    def trouver_suites_diff_variables(self, numeros, direction, params):
        """
        Trouve les suites qui suivent une logique arithmétique ou autre pattern reconnaissable.

        Args:
            numeros (list): Liste de nombres à analyser
            direction (str): "croissante", "decroissante" ou "tous" pour détecter les deux
            params (dict): Paramètres de recherche incluant 'min_elements' et 'forcer_min'

        Returns:
            list: Liste de tuples (suite, raisons) représentant les suites trouvées et leurs différences
        """
        suites = []
        n = len(numeros)

        # Fonction pour vérifier si une suite suit une progression logique
        def est_progression_logique(suite, raisons):
            # Progression arithmétique (différence constante)
            if all(r == raisons[0] for r in raisons):
                return True

            # Progression géométrique (ratio constant)
            if all(suite[i + 1] / suite[i] == suite[1] / suite[0] for i in range(len(suite) - 1)):
                return True

            # Suite de nombres pairs/impairs consécutifs
            if all(x % 2 == suite[0] % 2 for x in suite) and all(
                    abs(raisons[i + 1] - raisons[i]) <= 1 for i in range(len(raisons) - 1)):
                return True

            # Suite avec différences en progression arithmétique
            diffs_de_diffs = [raisons[i + 1] - raisons[i] for i in range(len(raisons) - 1)]
            if len(diffs_de_diffs) >= 2 and all(d == diffs_de_diffs[0] for d in diffs_de_diffs):
                return True

            return False

        # Pour chaque point de départ possible
        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                diff1 = numeros[j] - numeros[i]

                for k in range(j + 1, n):
                    diff2 = numeros[k] - numeros[j]

                    # Vérifier la direction des différences
                    direction_valide = (
                            direction == "tous" or
                            (direction == "croissante" and diff2 >= diff1) or
                            (direction == "decroissante" and diff2 <= diff1)
                    )

                    if direction_valide:
                        suite = [numeros[i], numeros[j], numeros[k]]
                        raisons = [diff1, diff2]
                        dernier = numeros[k]
                        derniere_diff = diff2

                        # Rechercher des numéros qui continuent la suite
                        for l in range(k + 1, n):
                            diff_courante = numeros[l] - dernier

                            # Vérifier si la différence suit la direction attendue
                            if ((direction == "tous") or
                                    (direction == "croissante" and diff_courante >= derniere_diff) or
                                    (direction == "decroissante" and diff_courante <= derniere_diff)):
                                suite.append(numeros[l])
                                raisons.append(diff_courante)
                                dernier = numeros[l]
                                derniere_diff = diff_courante

                        # Vérifier si la suite est assez longue et logique
                        if len(suite) >= params.get('min_elements', 3) or not params.get('forcer_min', True):
                            if est_progression_logique(suite, raisons):
                                suites.append((suite, raisons))

        return suites



    def _valide_direction(self, prev_diff, new_diff, direction):
        """Valide la cohérence des différences selon le motif"""
        if direction == "constante":
            return new_diff == prev_diff
        elif direction == "croissante":
            return new_diff > prev_diff
        elif direction == "decroissante":
            return new_diff < prev_diff
        return False

    def _respecte_critères(self, suite, params):
        """Vérifie les paramètres de longueur minimale"""
        return len(suite) >= params['min_elements'] or not params['forcer_min']

    def _filtrer_suites(self, suites):
        """Élimine les sous-suites incluses dans des suites plus longues"""
        suites.sort(key=lambda x: -len(x[0]))
        result = []
        seen = set()

        for suite, diffs in suites:
            suite_tuple = tuple(suite)
            if not any(suite_tuple in s for s in seen):
                seen.add(suite_tuple)
                result.append((suite, diffs))

        return result

    def est_premier(self, n):
        """Vérifie si un nombre est premier"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    def trouver_suites_nombres_premiers(self, numeros, params):
        """Trouve les suites constituées de nombres premiers consécutifs"""
        # Filtrer uniquement les nombres premiers
        nombres_premiers = [n for n in numeros if self.est_premier(n)]

        # Trier les nombres premiers
        nombres_premiers.sort()

        suites = []

        # Rechercher des séquences de nombres premiers consécutifs
        if len(nombres_premiers) >= params['min_elements']:
            i = 0
            while i < len(nombres_premiers):
                suite_courante = [nombres_premiers[i]]
                # Pour suivre les différences entre nombres premiers consécutifs
                raisons = []

                j = i + 1
                while j < len(nombres_premiers):
                    diff = nombres_premiers[j] - nombres_premiers[i]
                    suite_courante.append(nombres_premiers[j])
                    raisons.append(diff)
                    i = j
                    j += 1

                    # Vérifier si la suite est assez longue
                    if len(suite_courante) >= params['min_elements']:
                        suites.append((suite_courante, raisons))
                        break

                i += 1

        return suites

    def verifier_completion(self, suite):
        """
        Vérifie de manière exhaustive si une suite arithmétique est complète
        et identifie tous les nombres manquants possibles.
        Limite les numéros à 90 maximum (contrainte de loterie).
        """
        # Si la suite est vide ou trop courte, elle ne peut pas être analysée
        if len(suite) < 2:
            return []

        # Créer un ensemble pour les recherches rapides
        suite_set = set(suite)
        suite_triee = sorted(suite)

        # Calculer toutes les raisons possibles entre les éléments consécutifs
        raisons_candidates = []
        for i in range(len(suite_triee) - 1):
            raison = suite_triee[i + 1] - suite_triee[i]
            if raison != 0:  # Ignorer les raisons nulles
                raisons_candidates.append(raison)

        # S'il n'y a pas de raison candidate, impossible de détecter la complétion
        if not raisons_candidates:
            return []

        # La raison la plus fréquente est probablement la bonne
        from collections import Counter
        compteur_raisons = Counter(raisons_candidates)
        raison = compteur_raisons.most_common(1)[0][0]

        # Vérifier la cohérence avec cette raison
        # Une suite est valide si elle peut être représentée par a + n*r pour tous les éléments
        # où a est le premier terme et r est la raison

        # Trouver le premier terme théorique de la suite complète
        premier_terme = suite_triee[0]
        # Vérifier si on peut reculer encore plus
        while premier_terme - raison > 0:
            premier_terme -= raison

        # Générer tous les termes théoriques de la suite complète
        termes_theoriques = []
        terme_courant = premier_terme
        while terme_courant <= 90:  # Limite supérieure à 90
            termes_theoriques.append(terme_courant)
            terme_courant += raison

        # Identifier les termes manquants parmi les termes théoriques
        nombres_manquants = [terme for terme in termes_theoriques
                             if terme not in suite_set and
                             terme > 0 and terme <= 90]  # Assurer que les termes sont entre 1 et 90

        return sorted(nombres_manquants)

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
                        infos_suite = []  # Ajout pour uniformiser avec analyser_vertical

                        for num in suite:
                            for n_info in numeros_info:
                                if n_info[0] == num:
                                    colonnes_suite.append(n_info[1])
                                    # Créer le tuple d'informations comme dans analyser_vertical
                                    infos_suite.append(
                                        (n_info[0], ligne[self.index_date], ligne[self.index_type], n_info[1]))
                                    break

                        resultat = {
                            'date': ligne[self.index_date],
                            'type_tirage': ligne[self.index_type],
                            'type_suite': type_suite,
                            'suite': suite,
                            'colonnes': colonnes_suite,
                            'raisons': raisons,
                            'infos': infos_suite,  # Ajout pour uniformiser avec analyser_vertical
                            'sens': 'horizontal',
                            'position': None  # Ajout pour uniformiser (valeur None car pas applicable horizontalement)
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
        suites_deja_trouvees = set()  # Ensemble pour suivre les suites déjà trouvées

        for pos, numeros_info in numeros_par_position.items():
            if not params['respecter_position']:
                numeros_info.sort(key=lambda x: x[0], reverse=(params['ordre'] == "decroissant"))

            # Éliminer les doublons dans les numéros
            numeros_uniques_info = []
            numeros_vus = set()

            for info in numeros_info:
                if info[0] not in numeros_vus:
                    numeros_uniques_info.append(info)
                    numeros_vus.add(info[0])

            numeros = [n[0] for n in numeros_uniques_info]

            # Récupérer une date de référence (dernière date disponible)
            date_reference = numeros_uniques_info[-1][1] if numeros_uniques_info else ""
            type_tirage_reference = numeros_uniques_info[-1][2] if numeros_uniques_info else ""

            # Analyser selon les types de suites demandés
            for type_suite in params['types_suites']:
                suites_trouvees = self.identifier_suites(numeros, type_suite, params)

                for suite, raisons in suites_trouvees:
                    if suite and len(suite) >= params['min_elements']:
                        # Convertir la suite en tuple pour pouvoir la mettre dans un ensemble
                        suite_tuple = tuple(suite)

                        # Vérifier si cette suite a déjà été trouvée
                        if suite_tuple not in suites_deja_trouvees:
                            suites_deja_trouvees.add(suite_tuple)

                            # Trouver les informations associées à chaque numéro de la suite
                            infos_suite = []
                            colonnes_suite = []
                            for num in suite:
                                for n_info in numeros_info:
                                    if n_info[0] == num:
                                        infos_suite.append((n_info[0], n_info[1], n_info[2], n_info[3]))
                                        colonnes_suite.append(n_info[3])
                                        break

                            dates_suite = [info[1] for info in infos_suite]
                            date_plus_recente = max(dates_suite) if dates_suite else date_reference

                            resultat = {
                                'date': date_plus_recente,
                                'type_tirage': "Mixte",
                                'position': pos + 1,
                                'type_suite': type_suite,
                                'suite': suite,
                                'colonnes': colonnes_suite,
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

    def analyser_les_deux(self, donnees, params):
        """
        Analyse les suites à la fois horizontalement et verticalement,
        et combine les résultats des deux analyses.
        """
        # Stocker les résultats temporairement
        resultats_temp = self.resultats.copy()

        # Effectuer l'analyse horizontale
        self.analyser_horizontal(donnees, params)

        # Effectuer l'analyse verticale
        self.analyser_vertical(donnees, params)

        # Si nécessaire, fusionner ou traiter les résultats communs des deux analyses
        # Par exemple, identifier des schémas qui se répètent à la fois horizontalement et verticalement
        self.identifierSchemasCroises(resultats_temp)

    def identifierSchemasCroises(self, resultats_precedents):
        """
        Identifie les schémas qui se répètent à la fois horizontalement et verticalement.
        Cette fonction compare les nouveaux résultats (combinant horizontal et vertical)
        avec les résultats précédents pour identifier des patterns intéressants.

        Args:
            resultats_precedents: Les résultats avant l'analyse bidirectionnelle
        """
        # Analyser les resultats horizontaux et verticaux pour identifier des patterns
        resultats_horizontaux = [r for r in self.resultats if r['sens'] == 'horizontal']
        resultats_verticaux = [r for r in self.resultats if r['sens'] == 'vertical']

        # Rechercher des numéros qui apparaissent à la fois dans des suites horizontales et verticales
        numeros_horizontaux = set()
        for res in resultats_horizontaux:
            numeros_horizontaux.update(res['suite'])

        numeros_verticaux = set()
        for res in resultats_verticaux:
            numeros_verticaux.update(res['suite'])

        # Trouver l'intersection - numéros présents dans les deux analyses
        numeros_communs = numeros_horizontaux.intersection(numeros_verticaux)

        if numeros_communs:
            # Ajouter un résultat spécial pour les numéros communs
            self.resultats.append({
                'date': 'Multiple',
                'type_tirage': 'Analyse croisée',
                'type_suite': 'bidirectionnelle',
                'suite': sorted(list(numeros_communs)),
                'colonnes': ['Multiple'],
                'raisons': [],
                'sens': 'bidirectionnel',
                'position': None,
                'description': 'Numéros présents dans des suites à la fois horizontales et verticales'
            })

    def afficher_resultats(self):
        """Affiche les résultats de l'analyse"""
        if not self.resultats:
            print("Aucun résultat trouvé.")
            return

        print(f"\n=== RÉSULTATS DE L'ANALYSE ({len(self.resultats)} suites trouvées) ===\n")

        for i, res in enumerate(self.resultats, 1):
            print(f"Résultat #{i}:")

            if res['sens'] == 'horizontal':
                print(f"Sens d'analyse: Horizontal")
                print(f"Date: {res['date']}")
                print(f"Type de tirage: {res['type_tirage']}")

            elif res['sens'] == 'vertical':
                print(f"Sens d'analyse: Vertical")
                print(f"Position: {res['position']}")
                print("Infos: ", end="")
                for idx, info in enumerate(res['infos']):
                    if len(info) >= 4:  # Vérifier que nous avons bien 4 éléments
                        print(f"{info[0]} ({info[1]}, {info[2]}, {info[3]})", end=", ")
                    else:
                        print(f"{info[0]} ({info[1]}, {info[2]})", end=", ")
                print()

            elif res['sens'] == 'bidirectionnel':
                print(f"Sens d'analyse: Bidirectionnel")
                print(f"Date: {res['date']}")
                print(f"Type d'analyse: {res['type_tirage']}")
                if 'description' in res:
                    print(f"Description: {res['description']}")

            print(f"Type de suite: {res['type_suite']}")
            print(f"Suite: {res['suite']}")

            # Afficher les colonnes correspondantes
            print("Colonnes: ", end="")
            for col in res['colonnes']:
                print(f"{col}", end=", ")
            print()

            # Afficher les raisons si elles existent et ne sont pas vides
            if 'raisons' in res and res['raisons']:
                print(f"Raisons: {res['raisons']}")

            if 'complete' in res:
                print(f"Complète: {'Oui' if res['complete'] else 'Non'}")
                if not res['complete']:
                    print(f"Nombres manquants: {res['manquants']}")

            print()