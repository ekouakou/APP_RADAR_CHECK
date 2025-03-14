import json


class OpenAPIGenerator:
    def __init__(self):
        self.openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "L'analyse des suites arithmétiques",
                "description": "API pour l'analyse de données de loterie avec diverses options de filtrage.",
                "version": "1.0.0"
            },
            "servers": [
                {
                    "url": "http://127.0.0.1:5000",
                    "description": "Serveur local de développement"
                }
            ],
            "paths": {}
        }

    def determine_param_type(self, value):
        """
        Détermine le type du paramètre pour la documentation OpenAPI
        """
        if isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, str):
            return {"type": "string"}
        elif isinstance(value, list):
            # On suppose que ce sont des chaînes de caractères dans la liste
            return {
                "type": "array",
                "items": {"type": "string"}
            }
        else:
            return {"type": "string"}  # Valeur par défaut

    def generate_properties(self, example_params):
        """
        Génère dynamiquement la section 'properties' de la spécification OpenAPI avec des exemples et des valeurs par défaut
        """
        properties = {}
        for param, value in example_params.items():
            param_type = self.determine_param_type(value)
            description = f"Description pour {param}"  # Ici tu peux personnaliser les descriptions

            # Créer la structure avec 'example' et 'default' si nécessaire
            property_details = {
                **param_type,
                "description": description
            }

            # Ajouter 'example' si la valeur est fournie
            if param in example_params:
                property_details["example"] = example_params[param]

            # Ajouter 'default' pour les booléens ou les entiers (si nécessaire)
            if isinstance(value, bool) or isinstance(value, int):
                property_details["default"] = value

            properties[param] = property_details
        return properties

    def generate_request_body(self, example_params, with_file=False):
        """
        Génère dynamiquement le 'requestBody' pour l'OpenAPI
        """
        # Générer les propriétés dynamiquement pour le corps de la requête
        properties = self.generate_properties(example_params)

        # Structure pour multipart/form-data
        multipart_properties = {}

        if with_file:
            multipart_properties["file"] = {
                "type": "string",
                "format": "binary",
                "description": "Fichier CSV à analyser"
            }

        # Intégrer les autres paramètres dans multipart/form-data
        multipart_properties.update(properties)

        content_types = {}

        if with_file:
            content_types["multipart/form-data"] = {
                "schema": {
                    "type": "object",
                    "properties": multipart_properties
                }
            }

        content_types["application/json"] = {
            "schema": {
                "type": "object",
                "properties": properties
            }
        }

        if not with_file:
            content_types["application/x-www-form-urlencoded"] = {
                "schema": {
                    "type": "object",
                    "properties": properties
                }
            }

        return {
            "required": True,
            "content": content_types
        }

    def add_endpoint(self, api_path, http_method, summary, description, example_params, with_file=False,
                     responses=None):
        """
        Ajoute un endpoint à la spécification OpenAPI
        """
        # Générer le requestBody dynamiquement
        request_body = self.generate_request_body(example_params, with_file)

        # Responses par défaut si non spécifiées
        if responses is None:
            responses = {
                "200": {
                    "description": "Opération réussie",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "results": {"type": "array", "items": {"type": "object"}}
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Demande mal formulée"
                },
                "500": {
                    "description": "Erreur interne du serveur"
                }
            }

        # Créer l'entrée pour cet endpoint
        endpoint_spec = {
            "summary": summary,
            "description": description,
            "responses": responses
        }

        # Ajouter le requestBody pour les méthodes qui l'acceptent
        if http_method.upper() in ["POST", "PUT", "PATCH"]:
            endpoint_spec["requestBody"] = request_body

        # Ajouter l'endpoint au chemin
        if api_path not in self.openapi_spec["paths"]:
            self.openapi_spec["paths"][api_path] = {}

        self.openapi_spec["paths"][api_path][http_method.lower()] = endpoint_spec

    def save_spec(self, file_path="../../../../app_radar_check_reactjsVite_frontend/public/openapi_spec.json"):
        """
        Enregistre la spécification OpenAPI générée dans un fichier
        """
        with open(file_path, "w") as f:
            json.dump(self.openapi_spec, f, indent=2)


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le générateur
    generator = OpenAPIGenerator()

    # Ajouter l'endpoint /analyze (premier exemple)
    analyze_params = {
        'csv_path': './uploads/formatted_lottery_results.csv',
        'sens_lecture': True,
        'colonnes': "num",
        'respecter_positions': True,
        'types_tirage': None,
        'date_debut': None,
        'date_fin': None,
        'direction': "horizontal",
        'difference_constante': True,
        'respecter_ordre_apparition': False,
        'longueur_suite_filtre': None,
        'verifier_completion': True,
        'valeur_min': 1,
        'valeur_max': 90
    }

    generator.add_endpoint(
        api_path="/analyse_suites_arithmetiques/analyze",
        http_method="POST",
        summary="Analyser les suites arithmétiques",
        description="Point d'entrée API pour l'analyse des suites arithmétiques.",
        example_params=analyze_params
    )

    # Ajouter l'endpoint /lottery/health
    generator.add_endpoint(
        api_path="/analyse_suites_arithmetiques/lottery/health",
        http_method="GET",
        summary="Vérifier l'état de l'API",
        description="Point d'entrée API pour vérifier que l'API est opérationnelle.",
        example_params={}
    )

    # Ajouter l'endpoint /analyze (deuxième exemple)
    analyze_params_2 = {
        'file_path': './uploads/formatted_lottery_results.csv',
        'respect_columns': True,
        'page': 1,
        'per_page': 50,
        'min_sequence_length': 3,
        'max_results_per_date': 500,
        'search_depth': 'medium',
        'difference_type': 'constant',
        'respect_order': True,
        "filter_dates": ["01/02/2021","02/02/2021"],
        "filter_tirage_types": ["Reveil","Etoile","Akwaba"]
    }

    generator.add_endpoint(
        api_path="/analyse_suites_arithmetiques_jour/analyze",
        http_method="POST",
        summary="Analyser les données de loterie",
        description="Endpoint API pour l'analyse des données. Accepte un fichier CSV et divers paramètres de contrôle.",
        example_params=analyze_params_2,
        with_file=True
    )

    # Ajouter l'endpoint /analyze_lottery_data
    analyze_lottery_params = {
        'date_debut': '01/01/2025',
        'date_fin': '31/01/2025',
        'reverse_order': True,
        'longueur_min': 5,
        'type_analyse': None,
        'respecter_position': False,
        'analyser_meme_ligne': True,
        'fusionner_num_machine': False,
        'utiliser_longueur_min': False,
        'type_tirage': None,
        'file_path': './uploads/formatted_lottery_results.csv'
    }

    generator.add_endpoint(
        api_path="/analyze",
        http_method="POST",
        summary="Analyser les données de loterie",
        description="Endpoint API pour l'analyse des données de loterie.",
        example_params=analyze_lottery_params,
        with_file=True
    )

    # Ajouter l'endpoint /upload
    generator.add_endpoint(
        api_path="/upload",
        http_method="POST",
        summary="Télécharger un fichier",
        description="Endpoint pour télécharger un fichier CSV.",
        example_params={},
        with_file=True,
        responses={
            "200": {
                "description": "Fichier téléchargé avec succès",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "file_path": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Aucun fichier trouvé"
            }
        }
    )

    analyze_top = {
        "file_path": "./uploads/formatted_lottery_results.csv",
        "types_suites": ["arithmetique", "geometrique", "premiers"],
        "date_debut": "01/01/2020",
        "date_fin": "26/10/2022",
        "ordre": "decroissant",
        "min_elements": 4,
        "forcer_min": True,
        "verifier_completion": True,
        "respecter_position": False,
        "source_numeros": "tous",
        "ordre_lecture": "normal",
        "types_tirage": ["Reveil", "Sika"],
        "sens_analyse": "les_deux",
        "pagination": True,
        "items_par_page": 50,
        "page": 1
    }

    generator.add_endpoint(
        api_path="/api/suites/analyser",
        http_method="POST",
        summary="Télécharger un fichier",
        description="Endpoint pour télécharger un fichier CSV.",
        example_params=analyze_top,
        with_file=True,
        responses={
            "200": {
                "description": "Fichier téléchargé avec succès",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "file_path": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Aucun fichier trouvé"
            }
        }
    )

    # Générer le fichier OpenAPI
    generator.save_spec()