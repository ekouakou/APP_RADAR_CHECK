import React, { useState, useEffect } from 'react';
import axios from 'axios';
// import 'bootstrap/dist/css/bootstrap.min.css';
import './SuitesArithmetiques.css';

const SuitesArithmetiques = () => {
    const [suites, setSuites] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({
        totalSuites: 0,
        totalTiragesAvecSuites: 0
    });
    const [selectedType, setSelectedType] = useState('Tous');

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await axios.post(
                    'http://127.0.0.1:5000/analyse_suites_arithmetiques/analyze',
                    {
                        csv_path: "./uploads/formatted_lottery_results.csv",
                        sens_lecture: true,
                        colonnes: "num",
                        respecter_positions: true,
                        types_tirage: null,
                        // date_debut: "01/01/2022",
                        // date_fin: "01/02/2022",
                        direction: "vertical",
                        difference_constante: true,
                        respecter_ordre_apparition: false,
                        longueur_suite_filtre: null,
                        verifier_completion: true,
                        valeur_min: 1,
                        valeur_max: 90
                    }
                );

                setSuites(response.data.suites || []);
                setStats({
                    totalSuites: response.data.total_suites || 0,
                    totalTiragesAvecSuites: response.data.total_tirages_avec_suites || 0
                });
                setLoading(false);
            } catch (err) {
                setError('Erreur lors de la récupération des données: ' + err.message);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Récupérer tous les types uniques de suites
    const getUniqueTypes = () => {
        const allTypes = [];
        suites.forEach(suite => {
            if (suite.types && suite.types.length > 0) {
                suite.types.forEach(type => {
                    if (!allTypes.includes(type)) {
                        allTypes.push(type);
                    }
                });
            }
        });
        return allTypes;
    };

    // Filtrer les suites par type
    const filteredSuites = selectedType === 'Tous'
        ? suites
        : suites.filter(suite =>
            suite.types && suite.types.includes(selectedType)
        );

    // Obtenir la couleur correspondant au type
    const getTypeColorClass = (type) => {
        const typeColors = {
            'Baraka': 'type-baraka',
            'Awale': 'type-awale',
            'Etoile': 'type-etoile',
            'Fortune': 'type-fortune',
            'Benediction': 'type-benediction',
            'Monni': 'type-monni',
            'Soutra': 'type-soutra',
            'Nuit Etoilee': 'type-nuit-etoilee'
        };

        return typeColors[type] || '';
    };

    if (loading) return (
        <div className="container mt-5">
            <div className="d-flex justify-content-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Chargement...</span>
                </div>
            </div>
        </div>
    );

    if (error) return (
        <div className="container mt-5">
            <div className="alert alert-danger" role="alert">
                {error}
            </div>
        </div>
    );

    return (
        <div className="container-fluid p-4">
            <h1 className="mb-4">Analyse des Suites Arithmétiques</h1>

            {/* Résumé des statistiques */}
            <div className="card mb-4">
                <div className="card-header bg-light">
                    <h5 className="mb-0">Résumé</h5>
                </div>
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-6">
                            <div className="card">
                                <div className="card-body">
                                    <h6 className="card-subtitle mb-2 text-muted">Total des suites</h6>
                                    <h2 className="card-title">{stats.totalSuites}</h2>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-6">
                            <div className="card">
                                <div className="card-body">
                                    <h6 className="card-subtitle mb-2 text-muted">Tirages avec suites</h6>
                                    <h2 className="card-title">{stats.totalTiragesAvecSuites}</h2>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Filtres par type */}
            <div className="mb-4">
                <h5>Filtrer par type:</h5>
                <div className="d-flex flex-wrap gap-2">
                    <button
                        className={`btn ${selectedType === 'Tous' ? 'btn-primary' : 'btn-light'}`}
                        onClick={() => setSelectedType('Tous')}
                    >
                        Tous
                    </button>

                    {getUniqueTypes().map(type => (
                        <button
                            key={type}
                            className={`btn ${selectedType === type ? 'btn-primary' : 'btn-light'} ${getTypeColorClass(type)}`}
                            onClick={() => setSelectedType(type)}
                        >
                            {type}
                        </button>
                    ))}
                </div>
            </div>

            {/* Liste des suites */}
            {filteredSuites.length === 0 ? (
                <div className="alert alert-info">
                    Aucune suite arithmétique trouvée avec ces critères.
                </div>
            ) : (
                filteredSuites.map((suite, index) => {
                    const suiteType = suite.types && suite.types.length > 0 ? suite.types[0] : '';
                    const suiteDate = suite.dates && suite.dates.length > 0 ? suite.dates[0] : '';

                    return (
                        <div key={suite.cle || index} className="card mb-3">
                            <div className="card-header d-flex justify-content-between align-items-center">
                                <div className="d-flex align-items-center">
                                    <h5 className="mb-0">{suiteDate}</h5>
                                    <span className={`badge ms-2 ${getTypeColorClass(suiteType)}`}>
                                        {suiteType}
                                    </span>
                                </div>
                                <div className="d-flex align-items-center">
                                    <span className={`badge ${suite.est_complete ? 'bg-success' : 'bg-warning'} me-2`}>
                                        {suite.est_complete ? 'Complète' : 'Incomplète'}
                                    </span>
                                    <span className="text-muted">Raison: {suite.raison}</span>
                                </div>
                            </div>
                            <div className="card-body">
                                <div className="row">
                                    <div className="col-md-4">
                                        <p><strong>Valeurs:</strong> {suite.suite.join(', ')}</p>
                                        <p><strong>Colonnes:</strong> {suite.colonnes ? suite.colonnes.join(', ') : 'Non spécifié'}</p>
                                    </div>
                                    <div className="col-md-4">
                                        <p><strong>Type:</strong> {suite.type_suite}</p>
                                        <p><strong>Direction:</strong> {suite.direction}</p>
                                    </div>
                                    <div className="col-md-4">
                                        {suite.elements_manquants && suite.elements_manquants.length > 0 && (
                                            <div>
                                                <p><strong>Éléments manquants:</strong></p>
                                                <p className="text-danger">
                                                    {suite.elements_manquants.length > 10
                                                        ? `${suite.elements_manquants.slice(0, 10).join(', ')}... (${suite.elements_manquants.length} au total)`
                                                        : suite.elements_manquants.join(', ')}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })
            )}
        </div>
    );
};

export default SuitesArithmetiques;