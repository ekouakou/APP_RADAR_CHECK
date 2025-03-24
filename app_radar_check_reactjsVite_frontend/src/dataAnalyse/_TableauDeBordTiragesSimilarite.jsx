import React, { useState, useEffect } from 'react';
import { Table, Card, Row, Col, Statistic, Select, Input, Button, Pagination, Spin, Alert, Tag, Space, Divider } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { CalendarOutlined, NumberOutlined, SettingOutlined, SearchOutlined, LoadingOutlined } from '@ant-design/icons';

const { Option } = Select;

// Couleurs pour les graphiques
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const TableauDeBordTirages = () => {
  // États pour les données et filtres
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10); // Taille de page par défaut
  const [searchMode, setSearchMode] = useState('numbers');
  const [respectPositions, setRespectPositions] = useState('true');
  const [similarityThreshold, setSimilarityThreshold] = useState(0.4);
  const [drawLine, setDrawLine] = useState('01/01/2020;Lundi;janvier 2020;Premier;12;34;56;78;90;23;45;67;89;01');
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalResults: 0,
    typeDeTirageCount: {},
    monthlyDistribution: {}
  });

  // Fonction pour charger les données depuis l'API
  const fetchData = async (page = currentPage) => {
    setLoading(true);
    setError(null);
    
    try {
      // Préparer les paramètres pour l'API
      const params = {
        file_path: "./uploads/formatted_lottery_results.csv",
        action: "similar-draws",
        draw_line: drawLine,
        similarity_threshold: similarityThreshold,
        search_mode: searchMode,
        respect_positions: respectPositions,
        consider_proximity: "true",
        proximity_threshold: "2",
        items_per_page: pageSize,
        page: page
      };
      
      // Faire l'appel à l'API
      const response = await fetch('http://192.168.1.2:5007/api/allSimilarDrawsAndCombinationFinder', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
      });
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      
      const apiResponse = await response.json();
            
      setData(apiResponse.results);
      setTotalPages(apiResponse.total_pages);
      
      // Calculer les statistiques
      calculateStats(apiResponse.results, apiResponse.total_results);
      
    } catch (err) {
      setError("Erreur lors du chargement des données. Veuillez réessayer.");
      console.error("Erreur d'API:", err);
    } finally {
      setLoading(false);
    }
  };

  // Calculer des statistiques à partir des données
  const calculateStats = (results, totalResults) => {
    const typeDeTirageCount = {};
    const monthlyDistribution = {};
    
    results.forEach(item => {
      // Compter par type de tirage
      typeDeTirageCount[item['Type de Tirage']] = (typeDeTirageCount[item['Type de Tirage']] || 0) + 1;
      
      // Compter par mois
      monthlyDistribution[item.Mois] = (monthlyDistribution[item.Mois] || 0) + 1;
    });
    
    setStats({
      totalResults,
      typeDeTirageCount,
      monthlyDistribution
    });
  };

  // Formater les données pour les graphiques
  const getChartData = () => {
    return Object.entries(stats.typeDeTirageCount).map(([name, value]) => ({
      name,
      value
    }));
  };

  const getMonthlyChartData = () => {
    return Object.entries(stats.monthlyDistribution).map(([name, value]) => ({
      name,
      value
    }));
  };

  // Colonnes pour le tableau
  const columns = [
    {
      title: 'Date',
      dataIndex: 'Date',
      key: 'date',
      render: text => new Date(text).toLocaleDateString('fr-FR')
    },
    {
      title: 'Jour',
      dataIndex: 'Jour',
      key: 'jour',
    },
    {
      title: 'Type de Tirage',
      dataIndex: 'Type de Tirage',
      key: 'type',
      render: text => <Tag color="blue">{text}</Tag>
    },
    {
      title: 'Numéros',
      key: 'numeros',
      render: (_, record) => (
        <Space>
          {[1, 2, 3, 4, 5].map(i => (
            <Tag color="green" key={`num${i}`}>{record[`Num${i}`]}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: 'Machines',
      key: 'machines',
      render: (_, record) => (
        <Space>
          {[1, 2, 3, 4, 5].map(i => (
            <Tag color="volcano" key={`machine${i}`}>{record[`Machine${i}`]}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: 'Similarité',
      dataIndex: 'similarity',
      key: 'similarity',
      render: text => `${(text * 100).toFixed(0)}%`
    }
  ];

  // Charger les données au montage du composant
  useEffect(() => {
    fetchData(1); // Charger la première page au début
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Gérer le changement de page
  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchData(page); // Passer explicitement la nouvelle page
  };

  // Gérer la recherche
  const handleSearch = () => {
    setCurrentPage(1); // Réinitialiser à la première page lors d'une nouvelle recherche
    fetchData(1);
  };

  return (
    <div className="p-4 bg-gray-50 min-h-screen">
      <Card className="mb-4 shadow-sm">
        <h1 className="text-2xl font-bold mb-2 text-blue-800">Tableau de Bord des Tirages Similaires</h1>
        <Divider />
        
        {/* Filtres de recherche */}
        <Row gutter={16} className="mb-4">
          <Col xs={24} md={12} lg={8}>
            <div className="mb-2">Ligne de tirage</div>
            <Input 
              placeholder="Format: DD/MM/YYYY;Jour;mois YYYY;Type;N1;N2;N3;N4;N5;M1;M2;M3;M4;M5" 
              value={drawLine}
              onChange={e => setDrawLine(e.target.value)}
              className="mb-3"
            />
          </Col>
          <Col xs={24} md={6} lg={4}>
            <div className="mb-2">Mode de recherche</div>
            <Select 
              value={searchMode} 
              onChange={setSearchMode}
              className="w-full mb-3"
            >
              <Option value="numbers">Numéros</Option>
              <Option value="machines">Machines</Option>
              <Option value="both">Les deux</Option>
            </Select>
          </Col>
          <Col xs={24} md={6} lg={4}>
            <div className="mb-2">Respecter les positions</div>
            <Select 
              value={respectPositions} 
              onChange={setRespectPositions}
              className="w-full mb-3"
            >
              <Option value="true">Oui</Option>
              <Option value="false">Non</Option>
            </Select>
          </Col>
          <Col xs={24} md={6} lg={4}>
            <div className="mb-2">Seuil de similarité</div>
            <Select 
              value={similarityThreshold} 
              onChange={setSimilarityThreshold}
              className="w-full mb-3"
            >
              <Option value={0.2}>20%</Option>
              <Option value={0.4}>40%</Option>
              <Option value={0.6}>60%</Option>
              <Option value={0.8}>80%</Option>
            </Select>
          </Col>
          <Col xs={24} md={6} lg={4}>
            <div className="mb-2">&nbsp;</div>
            <Button 
              type="primary" 
              icon={<SearchOutlined />} 
              onClick={handleSearch}
              className="w-full"
            >
              Rechercher
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Statistiques */}
      <Row gutter={16} className="mb-4">
        <Col xs={24} md={8}>
          <Card className="shadow-sm">
            <Statistic 
              title="Total des résultats" 
              value={stats.totalResults} 
              prefix={<NumberOutlined />} 
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="shadow-sm">
            <Statistic 
              title="Types de tirage" 
              value={Object.keys(stats.typeDeTirageCount).length} 
              prefix={<SettingOutlined />} 
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="shadow-sm">
            <Statistic 
              title="Périodes couvertes" 
              value={Object.keys(stats.monthlyDistribution).length} 
              prefix={<CalendarOutlined />} 
            />
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={16} className="mb-4">
        <Col xs={24} md={12}>
          <Card title="Répartition par Type de Tirage" className="shadow-sm">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Répartition par Mois" className="shadow-sm">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={getMonthlyChartData()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {getMonthlyChartData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Tableau des résultats */}
      <Card className="shadow-sm">
        <h2 className="text-xl font-bold mb-4">Résultats des Tirages Similaires</h2>
        
        {error && <Alert message={error} type="error" className="mb-4" />}
        
        {loading ? (
          <div className="text-center py-8">
            <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
            <div className="mt-2">Chargement des données...</div>
          </div>
        ) : (
          <>
            <Table 
              dataSource={data} 
              columns={columns} 
              rowKey={(record) => record.Date + record['Type de Tirage']}
              pagination={false}
              className="mb-4"
            />
            
            <div className="flex justify-end">
              <Pagination 
                current={currentPage} 
                total={stats.totalResults} 
                pageSize={pageSize} 
                onChange={handlePageChange} 
                showSizeChanger={false}
              />
            </div>
          </>
        )}
      </Card>

      <div className="text-center text-gray-500 mt-8">
        © 2025 Système d'Analyse de Tirages - Tous droits réservés
      </div>
    </div>
  );
};

export default TableauDeBordTirages;