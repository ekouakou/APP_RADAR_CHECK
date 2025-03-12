import json

class OpenAPIGenerator:
    def __init__(self, example_params, api_path="/analyze", http_method="POST"):
        self.example_params = example_params
        self.api_path = api_path  # Le path est maintenant dynamique
        self.http_method = http_method.upper()  # Utilisation du type de requête (POST, GET, etc.)
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

    def generate_properties(self):
        """
        Génère dynamiquement la section 'properties' de la spécification OpenAPI avec des exemples et des valeurs par défaut
        """
        properties = {}
        for param, value in self.example_params.items():
            param_type = self.determine_param_type(value)
            description = f"Description pour {param}"  # Ici tu peux personnaliser les descriptions

            # Créer la structure avec 'example' et 'default' si nécessaire
            property_details = {
                **param_type,
                "description": description
            }

            # Ajouter 'example' si la valeur est fournie
            if param in self.example_params:
                property_details["example"] = self.example_params[param]

            # Ajouter 'default' pour les booléens ou les entiers (si nécessaire)
            if isinstance(value, bool) or isinstance(value, int):
                property_details["default"] = value

            properties[param] = property_details
        return properties

    def generate_request_body(self):
        """
        Génère dynamiquement le 'requestBody' pour l'OpenAPI
        """
        # Générer les propriétés dynamiquement pour le corps de la requête
        properties = self.generate_properties()

        # Structure pour multipart/form-data
        multipart_properties = {
            "file": {
                "type": "string",
                "format": "binary",
                "description": "Fichier CSV à analyser"
            }
        }

        # Intégrer les autres paramètres dans multipart/form-data
        multipart_properties.update(properties)

        return {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": multipart_properties
                    }
                },
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": properties
                    }
                }
            }
        }

    def generate_openapi_spec(self):
        """
        Génère la spécification OpenAPI avec les paramètres dynamiques et un path dynamique
        """
        # Générer le requestBody dynamiquement
        request_body = self.generate_request_body()

        # Créer la spécification de l'API pour l'endpoint dynamique
        self.openapi_spec["paths"][self.api_path] = {
            self.http_method.lower(): {  # Utilisation dynamique du type de méthode
                "summary": "Analyser les suites arithmétiques",
                "description": "Analyse un fichier CSV pour détecter des suites arithmétiques avec divers filtres.",
                "requestBody": request_body,
                "responses": {
                    "200": {
                        "description": "Analyse réussie",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "config": {
                                            "type": "object"
                                        },
                                        "pagination": {
                                            "type": "object"
                                        },
                                        "results": {
                                            "type": "array",
                                            "items": {
                                                "type": "object"
                                            }
                                        }
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
            }
        }

    def save_spec(self, file_path="openapi_spec.json"):
        """
        Enregistre la spécification OpenAPI générée dans un fichier
        """
        with open(file_path, "w") as f:
            json.dump(self.openapi_spec, f, indent=2)

# Exemple d'utilisation de la classe OpenAPIGenerator
if __name__ == "__main__":
    # Exemple de paramètres pour le premier endpoint
    example_params_1 = {
        "file_path": "./uploads/formatted_lottery_results.csv",
        "date_debut": "01/01/2020",
        "date_fin": "31/12/2020",
        "type_tirage": "LOTO",
        "longueur_min": 3,
        "type_analyse": "progression",
        "respecter_position": True,
        "analyser_meme_ligne": False,
        "fusionner_num_machine": False,
        "utiliser_longueur_min": True,
        "reverse_order": False
    }

    # Exemple de paramètres pour le deuxième endpoint
    example_params_2 = {
        "file_path": "./uploads/lottery_results_v2.csv",
        "date_debut": "01/01/2021",
        "date_fin": "31/12/2021",
        "type_tirage": "EUROJACKPOT",
        "longueur_min": 4,
        "type_analyse": "regression",
        "respecter_position": False,
        "analyser_meme_ligne": True,
        "fusionner_num_machine": True,
        "utiliser_longueur_min": False,
        "reverse_order": True
    }

    # Créer une instance de OpenAPIGenerator pour le premier endpoint
    api_generator_1 = OpenAPIGenerator(example_params_1, api_path="/progress_regress_constantes/analyze", http_method="POST")

    # Générer la spécification OpenAPI pour le premier endpoint
    api_generator_1.generate_openapi_spec()

    # Créer une instance de OpenAPIGenerator pour le deuxième endpoint
    api_generator_2 = OpenAPIGenerator(example_params_2, api_path="/analyze_v2", http_method="GET")

    # Générer la spécification OpenAPI pour le deuxième endpoint
    api_generator_2.generate_openapi_spec()

    # Fusionner les spécifications des deux générateurs
    api_generator_1.openapi_spec["paths"].update(api_generator_2.openapi_spec["paths"])

    # Sauvegarder la spécification dans un fichier avec les deux endpoints
    api_generator_1.save_spec("openapi_spec.json")
