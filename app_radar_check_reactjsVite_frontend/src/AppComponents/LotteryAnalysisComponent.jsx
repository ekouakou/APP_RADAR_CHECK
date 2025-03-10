import React, { useState } from 'react';
import axios from 'axios';

const LotteryAnalysisComponent = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    file_path: './uploads/formatted_lottery_results.csv',
    date_debut: '01/01/2020',
    date_fin: '31/12/2020',
    type_tirage: '',
    longueur_min: 3,
    type_analyse: 'progression',
    respecter_position: true,
    analyser_meme_ligne: false,
    fusionner_num_machine: false,
    utiliser_longueur_min: true,
    reverse_order: false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/analyze', formData);
      setData(response.data);
    } catch (err) {
      setError('Erreur lors de la récupération des données: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour vérifier si un objet a des données pertinentes
  const hasData = (obj) => {
    if (!obj) return false;
    
    // Pour un tableau, vérifier s'il contient des éléments
    if (Array.isArray(obj)) {
      return obj.length > 0;
    }
    
    // Pour un objet, vérifier récursivement s'il contient des données pertinentes
    if (typeof obj === 'object') {
      for (const key in obj) {
        if (hasData(obj[key])) {
          return true;
        }
      }
    }
    
    return false;
  };

  const renderProgressions = (progressions) => {
    if (!progressions || progressions.length === 0) {
      return null;
    }

    return progressions.map((prog, idx) => (
      <div key={idx} className="bg-white p-4 rounded-lg shadow mb-4">
        <h4 className="font-semibold mb-2">Progression {idx + 1}</h4>
        
        {Object.entries(prog).map(([key, value]) => {
          // Afficher différemment selon le type de valeur
          if (Array.isArray(value)) {
            return (
              <div key={key} className="mt-2">
                <p className="font-medium">{key.charAt(0).toUpperCase() + key.slice(1)}:</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {value.map((val, vidx) => (
                    <span key={vidx} className={`
                      ${key === 'valeurs' ? 'bg-blue-100 text-blue-800' : 
                        key === 'types' ? 'bg-purple-100 text-purple-800' : 
                        key === 'dates' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }
                      px-2 py-1 rounded
                    `}>
                      {val}
                    </span>
                  ))}
                </div>
              </div>
            );
          } else {
            return (
              <p key={key}>
                <span className="font-medium">{key.charAt(0).toUpperCase() + key.slice(1)}:</span> {value}
              </p>
            );
          }
        })}
      </div>
    ));
  };

  const renderPositionData = (positionData, position) => {
    if (!positionData) return null;
    
    // Vérifier si la position a des données non vides
    const hasProg = hasData(positionData.progressions_constantes);
    const hasReg = hasData(positionData.regressions_constantes);
    
    if (!hasProg && !hasReg) return null;
    
    return (
      <div key={position} className="mb-4 ml-4">
        <h4 className="text-md font-medium mb-2 text-blue-600">{position}</h4>
        
        <div className="ml-4">
          {hasProg && (
            <div className="mb-3">
              <h5 className="font-medium text-green-700 mb-2">Progressions Constantes</h5>
              {renderProgressions(positionData.progressions_constantes)}
            </div>
          )}
          
          {hasReg && (
            <div className="mb-3">
              <h5 className="font-medium text-red-700 mb-2">Régressions Constantes</h5>
              {renderProgressions(positionData.regressions_constantes)}
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderGameTypeData = (gameTypeData, gameType) => {
    if (!gameTypeData) return null;
    
    // Filtrer les positions qui ont des données
    const positionsWithData = Object.keys(gameTypeData).filter(position => 
      hasData(gameTypeData[position].progressions_constantes) || 
      hasData(gameTypeData[position].regressions_constantes)
    );
    
    if (positionsWithData.length === 0) return null;
    
    return (
      <div key={gameType} className="mb-4">
        <h3 className="text-lg font-semibold mb-2 bg-gray-100 p-2 rounded">{gameType}</h3>
        
        {positionsWithData.map(position => 
          renderPositionData(gameTypeData[position], position)
        )}
      </div>
    );
  };

  const renderCategoryData = (categoryData, categoryName) => {
    if (!categoryData) return null;
    
    // Filtrer les types de jeu qui ont des données
    const gameTypesWithData = Object.keys(categoryData).filter(gameType => {
      const positions = Object.keys(categoryData[gameType]);
      return positions.some(position => 
        hasData(categoryData[gameType][position].progressions_constantes) || 
        hasData(categoryData[gameType][position].regressions_constantes)
      );
    });
    
    if (gameTypesWithData.length === 0) return null;
    
    return (
      <div className="mb-6">
        <h3 className="text-xl font-bold mb-4 border-b pb-2">{categoryName}</h3>
        
        {gameTypesWithData.map(gameType => 
          renderGameTypeData(categoryData[gameType], gameType)
        )}
      </div>
    );
  };

  const renderResults = () => {
    if (!data) return null;
    
    // Identifier dynamiquement les catégories principales de données
    const categories = Object.keys(data);
    
    return (
      <div className="bg-white shadow-md rounded p-6">
        <h2 className="text-xl font-semibold mb-4">Résultats de l'analyse</h2>
        
        {categories.map(category => {
          // Nommer les catégories de manière conviviale
          const categoryDisplayName = {
            'machine': 'Machine',
            'num': 'Numéros'
          }[category] || category;
          
          return renderCategoryData(data[category], categoryDisplayName);
        })}
        
        {categories.length === 0 && (
          <p className="text-gray-500">Aucune donnée trouvée avec les paramètres actuels</p>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Analyse de Loterie</h1>
      
      <div className="bg-white shadow-md rounded p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Paramètres</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Chemin du fichier</label>
            <input
              type="text"
              name="file_path"
              value={formData.file_path}
              onChange={handleChange}
              className="w-full border rounded p-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Type de tirage</label>
            <input
              type="text"
              name="type_tirage"
              value={formData.type_tirage}
              onChange={handleChange}
              className="w-full border rounded p-2"
              placeholder="Laissez vide pour tous les types"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Date début</label>
            <input
              type="text"
              name="date_debut"
              value={formData.date_debut}
              onChange={handleChange}
              className="w-full border rounded p-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Date fin</label>
            <input
              type="text"
              name="date_fin"
              value={formData.date_fin}
              onChange={handleChange}
              className="w-full border rounded p-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Longueur minimale</label>
            <input
              type="number"
              name="longueur_min"
              value={formData.longueur_min}
              onChange={handleChange}
              className="w-full border rounded p-2"
              min="2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Type d'analyse</label>
            <select
              name="type_analyse"
              value={formData.type_analyse}
              onChange={handleChange}
              className="w-full border rounded p-2"
            >
              <option value="progression">Progression</option>
              <option value="regression">Régression</option>
              <option value="all">Tous</option>
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="respecter_position"
                checked={formData.respecter_position}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Respecter la position</span>
            </label>
          </div>
          
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="analyser_meme_ligne"
                checked={formData.analyser_meme_ligne}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Analyser même ligne</span>
            </label>
          </div>
          
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="fusionner_num_machine"
                checked={formData.fusionner_num_machine}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Fusionner numéros et machine</span>
            </label>
          </div>
          
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="utiliser_longueur_min"
                checked={formData.utiliser_longueur_min}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Utiliser longueur minimale</span>
            </label>
          </div>
          
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="reverse_order"
                checked={formData.reverse_order}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Ordre inversé</span>
            </label>
          </div>
        </div>
        
        <button 
          onClick={fetchData} 
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
          disabled={loading}
        >
          {loading ? 'Chargement...' : 'Analyser les données'}
        </button>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {data && renderResults()}
    </div>
  );
};

export default LotteryAnalysisComponent;