import React, { useState, useEffect } from 'react';
import { Table, Card, Tag, Select, Switch, Radio, Input, Pagination, Tabs, Spin, Button, Space, Tooltip, Statistic, Row, Col, Badge, Segmented, Divider, Collapse } from 'antd';
import { SearchOutlined, FilterOutlined, CalendarOutlined, ReloadOutlined, SettingOutlined, InfoCircleOutlined, DownloadOutlined } from '@ant-design/icons';
import { BarChart2, LineChart as LineChartIcon, Table as TableIcon, SortAsc, SortDesc, RefreshCw, Settings, Sun, Moon } from 'lucide-react';
import { LineChart, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, Line, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const { TabPane } = Tabs;
const { Option } = Select;
const { Panel } = Collapse;

const LotteryDashboard = () => {
  // États
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 });
  const [filters, setFilters] = useState({
    typeSuite: ['arithmetique', 'geometrique', 'premiers'],
    typeTirage: ['Reveil', 'Sika'],
    sens: 'les_deux',
    dateDebut: '06/01/2025',
    dateFin: '06/01/2025',
    minElements: 4,
    forcerMin: true,
    verifierCompletion: true,
    respecterPosition: false,
    sourceNumeros: 'tous',
    ordreLecture: 'normal'
  });
  const [sortOrder, setSortOrder] = useState('decroissant');
  const [darkMode, setDarkMode] = useState(false);
  const [viewMode, setViewMode] = useState('table');
  const [searchText, setSearchText] = useState('');
  
  // Pour les statistiques
  const [stats, setStats] = useState({
    totalSuites: 0,
    completesSuites: 0,
    suitesParType: {},
    suitesParTirage: {},
    numerosFréquents: []
  });

  // Effet pour charger les données
  useEffect(() => {
    fetchData();
  }, [pagination.current, filters, sortOrder]);

  // Fonction pour récupérer les données depuis l'API
  const fetchData = async () => {
    setLoading(true);
    
    try {
      const requestData = {
        file_path: "./uploads/formatted_lottery_results.csv",
        types_suites: filters.typeSuite,
        date_debut: filters.dateDebut,
        date_fin: filters.dateFin,
        ordre: sortOrder,
        min_elements: filters.minElements,
        forcer_min: filters.forcerMin,
        verifier_completion: filters.verifierCompletion,
        respecter_position: filters.respecterPosition,
        source_numeros: filters.sourceNumeros,
        ordre_lecture: filters.ordreLecture,
        types_tirage: filters.typeTirage,
        sens_analyse: filters.sens,
        pagination: true,
        items_par_page: pagination.pageSize,
        page: pagination.current
      };
      
      const response = await axios.post('http://192.168.1.2:5007/api/allSuiteFinder', requestData);
      
      // Si la recherche est active, filtrer les résultats
      let filteredData = response.data.resultats;
      if (searchText) {
        filteredData = filteredData.filter(item => {
          const searchLower = searchText.toLowerCase();
          return (
            (item.type_suite && item.type_suite.toLowerCase().includes(searchLower)) ||
            (item.type_tirage && item.type_tirage.toLowerCase().includes(searchLower)) ||
            (item.suite && item.suite.some(num => num.toString().includes(searchText)))
          );
        });
      }
      
      setData(filteredData);
      setPagination({
        ...pagination,
        total: response.data.total_resultats,
      });
      
      // Calculer les statistiques
      calculateStats(filteredData);
      
    } catch (error) {
      console.error('Erreur lors de la récupération des données:', error);
      // En cas d'erreur, utiliser des données fictives pour la démo
      const mockData = mockApiCall();
      setData(mockData.resultats);
      setPagination({
        ...pagination,
        total: mockData.total_resultats,
      });
      calculateStats(mockData.resultats);
    } finally {
      setLoading(false);
    }
  };
  
  // Fonction de secours avec données fictives
  const mockApiCall = () => {
    const jsonData = {
      "page_courante": 1,
      "resultats": [
        {
          "colonnes": ["Num2", "Machine3", "Num4", "Machine2"],
          "complete": false,
          "date": "20/10/2020",
          "infos": [
            [47, "20/10/2020", "Sika", "Num2"],
            [43, "20/10/2020", "Sika", "Machine3"],
            [39, "20/10/2020", "Sika", "Num4"],
            [35, "20/10/2020", "Sika", "Machine2"]
          ],
          "manquants": [3, 7, 11, 15, 19, 23, 27, 31, 51, 55, 59, 63, 67, 71, 75, 79, 83, 87],
          "position": null,
          "raisons": [-4, -4, -4],
          "sens": "horizontal",
          "suite": [47, 43, 39, 35],
          "type_suite": "arithmetique",
          "type_tirage": "Sika"
        }
      ],
      "total_pages": 1,
      "total_resultats": 1
    };
    
    return jsonData;
  };
  
  // Calculer les statistiques
  const calculateStats = (resultats) => {
    const completes = resultats.filter(item => item.complete).length;
    
    // Compter par type de suite
    const typesSuite = {};
    resultats.forEach(item => {
      if (item.type_suite) {
        typesSuite[item.type_suite] = (typesSuite[item.type_suite] || 0) + 1;
      }
    });
    
    // Compter par type de tirage
    const typesTirage = {};
    resultats.forEach(item => {
      if (item.type_tirage) {
        typesTirage[item.type_tirage] = (typesTirage[item.type_tirage] || 0) + 1;
      }
    });
    
    // Trouver les numéros les plus fréquents
    const numerosCount = {};
    resultats.forEach(item => {
      if (item.suite) {
        item.suite.forEach(num => {
          numerosCount[num] = (numerosCount[num] || 0) + 1;
        });
      }
    });
    
    const numerosFréquents = Object.entries(numerosCount)
      .map(([numero, count]) => ({ numero: parseInt(numero), count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
    
    setStats({
      totalSuites: resultats.length,
      completesSuites: completes,
      suitesParType: typesSuite,
      suitesParTirage: typesTirage,
      numerosFréquents
    });
  };

  // Préparer les données pour les graphiques
  const prepareChartData = () => {
    // Pour le graphique des types de suites
    const typeSuiteData = Object.entries(stats.suitesParType).map(([name, value]) => ({ name, value }));
    
    // Pour le graphique des types de tirage
    const typeTirageData = Object.entries(stats.suitesParTirage).map(([name, value]) => ({ name, value }));
    
    // Pour le graphique des numéros fréquents
    const numerosFréquentsData = stats.numerosFréquents.map(item => ({
      name: item.numero.toString(),
      value: item.count
    }));
    
    return {
      typeSuiteData,
      typeTirageData,
      numerosFréquentsData
    };
  };

  // Rendu des infos détaillées
  const renderInfoDetails = (infos) => {
    if (!infos || !infos.length) return null;
    
    const columns = [
      { title: 'Numéro', dataIndex: 0, key: 'numero' },
      { title: 'Date', dataIndex: 1, key: 'date' },
      { title: 'Type', dataIndex: 2, key: 'type' },
      { title: 'Position', dataIndex: 3, key: 'position' }
    ];
    
    return (
      <Table 
        dataSource={infos}
        columns={columns}
        pagination={false}
        size="small"
        rowKey={(record, index) => `info-${index}`}
      />
    );
  };
  
  // Rendu des numéros manquants
  const renderManquants = (manquants) => {
    if (!manquants || !manquants.length) return <span>Aucun</span>;
    
    return (
      <div className="flex flex-wrap gap-1">
        {manquants.map((num, index) => (
          <Tag key={index} color="red">{num}</Tag>
        ))}
      </div>
    );
  };

  // Définition des colonnes du tableau
  const columns = [
    {
      title: 'Type',
      dataIndex: 'type_suite',
      key: 'type_suite',
      render: (text) => {
        let color = 'blue';
        if (text === 'arithmetique') color = 'green';
        if (text === 'premiers') color = 'purple';
        if (text === 'geometrique') color = 'orange';
        if (text === 'bidirectionnelle') color = 'red';
        return <Tag color={color}>{text}</Tag>;
      },
      sorter: (a, b) => a.type_suite.localeCompare(b.type_suite),
    },
    {
      title: 'Tirage',
      dataIndex: 'type_tirage',
      key: 'type_tirage',
      render: (text) => {
        let color = 'cyan';
        if (text === 'Sika') color = 'volcano';
        if (text === 'Reveil') color = 'geekblue';
        if (text === 'Mixte') color = 'magenta';
        if (text === 'Analyse croisée') color = 'gold';
        return <Tag color={color}>{text}</Tag>;
      },
      sorter: (a, b) => a.type_tirage.localeCompare(b.type_tirage),
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      sorter: (a, b) => new Date(a.date.split('/').reverse().join('-')) - new Date(b.date.split('/').reverse().join('-')),
    },
    {
      title: 'Sens',
      dataIndex: 'sens',
      key: 'sens',
      render: (text) => {
        let color = 'blue';
        if (text === 'horizontal') color = 'cyan';
        if (text === 'vertical') color = 'lime';
        if (text === 'bidirectionnel') color = 'orange';
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: 'Suite',
      dataIndex: 'suite',
      key: 'suite',
      render: (suite) => (
        <div className="flex flex-wrap gap-1">
          {suite && suite.map((num, index) => (
            <Tag key={index} color="blue">{num}</Tag>
          ))}
        </div>
      ),
    },
    {
      title: 'Complète',
      dataIndex: 'complete',
      key: 'complete',
      render: (complete) => (
        <Badge status={complete ? "success" : "warning"} text={complete ? "Oui" : "Non"} />
      ),
      sorter: (a, b) => (a.complete === b.complete ? 0 : a.complete ? -1 : 1),
    },
    {
      title: 'Raisons',
      dataIndex: 'raisons',
      key: 'raisons',
      render: (raisons) => (
        <div className="flex flex-wrap gap-1">
          {raisons && raisons.map((raison, index) => (
            <Tag key={index} color={raison < 0 ? "red" : "green"}>{raison}</Tag>
          ))}
        </div>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="Détails">
            <Button 
              size="small" 
              shape="circle" 
              icon={<InfoCircleOutlined />} 
              onClick={() => {
                // Créer un state local pour gérer l'affichage des détails
                // ou utiliser un modal pour afficher tous les détails
              }} 
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // Gérer le changement de page
  const handlePageChange = (page, pageSize) => {
    setPagination({
      ...pagination,
      current: page,
      pageSize: pageSize,
    });
  };

  // Gérer les changements de filtres
  const handleFilterChange = (key, value) => {
    setFilters({
      ...filters,
      [key]: value,
    });
    setPagination({
      ...pagination,
      current: 1, // Retour à la première page lors d'un changement de filtre
    });
  };

  // Gérer le changement de thème
  const toggleTheme = () => {
    setDarkMode(!darkMode);
    // Appliquer les classes CSS pour le thème sombre
    document.body.classList.toggle('dark-theme');
  };

  // Pour le rendu des données sous forme de carte
  const renderCardView = () => {
    return (
      <Row gutter={[16, 16]}>
        {data.map((item, index) => (
          <Col xs={24} sm={12} md={8} lg={6} key={index}>
            <Card 
              title={
                <div className="flex items-center">
                  <Tag color={item.type_suite === 'arithmetique' ? 'green' : item.type_suite === 'premiers' ? 'purple' : 'orange'}>
                    {item.type_suite}
                  </Tag>
                  <span className="ml-2">{item.date}</span>
                </div>
              }
              bordered={true}
              className={darkMode ? "bg-gray-800 text-white" : ""}
              extra={<Badge status={item.complete ? "success" : "warning"} text={item.complete ? "Complète" : "Incomplète"} />}
            >
              <p><strong>Tirage:</strong> 
                <Tag color={item.type_tirage === 'Sika' ? 'volcano' : 'geekblue'} className="ml-2">
                  {item.type_tirage}
                </Tag>
              </p>
              <p><strong>Sens:</strong> 
                <Tag color={item.sens === 'horizontal' ? 'cyan' : 'lime'} className="ml-2">
                  {item.sens}
                </Tag>
              </p>
              <p><strong>Suite:</strong></p>
              <div className="flex flex-wrap gap-1 mb-2">
                {item.suite && item.suite.map((num, idx) => (
                  <Tag key={idx} color="blue">{num}</Tag>
                ))}
              </div>
              <p><strong>Raisons:</strong></p>
              <div className="flex flex-wrap gap-1 mb-2">
                {item.raisons && item.raisons.map((raison, idx) => (
                  <Tag key={idx} color={raison < 0 ? "red" : "green"}>{raison}</Tag>
                ))}
              </div>
              
              <Collapse ghost>
                <Panel header="Détails supplémentaires" key="1">
                  <p><strong>Colonnes:</strong></p>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {item.colonnes && item.colonnes.map((col, idx) => (
                      <Tag key={idx} color="blue">{col}</Tag>
                    ))}
                  </div>
                  
                  <p><strong>Numéros manquants:</strong></p>
                  {renderManquants(item.manquants)}
                  
                  <Divider orientation="left" plain>Infos détaillées</Divider>
                  {renderInfoDetails(item.infos)}
                </Panel>
              </Collapse>
            </Card>
          </Col>
        ))}
      </Row>
    );
  };

  // Pour le rendu des données sous forme de graphique
  const renderChartView = () => {
    const chartData = prepareChartData();
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

    return (
      <div>
        <Row gutter={[16, 24]}>
          <Col xs={24} md={12}>
            <Card title="Répartition par Type de Suite" bordered={true} className={darkMode ? "bg-gray-800 text-white" : ""}>
              <PieChart width={300} height={300}>
                <Pie
                  data={chartData.typeSuiteData}
                  cx={150}
                  cy={150}
                  labelLine={true}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {chartData.typeSuiteData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend />
              </PieChart>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="Répartition par Type de Tirage" bordered={true} className={darkMode ? "bg-gray-800 text-white" : ""}>
              <PieChart width={300} height={300}>
                <Pie
                  data={chartData.typeTirageData}
                  cx={150}
                  cy={150}
                  labelLine={true}
                  outerRadius={80}
                  fill="#82ca9d"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {chartData.typeTirageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend />
              </PieChart>
            </Card>
          </Col>
          <Col xs={24}>
            <Card title="Numéros les plus fréquents" bordered={true} className={darkMode ? "bg-gray-800 text-white" : ""}>
              <BarChart width={700} height={300} data={chartData.numerosFréquentsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8" name="Fréquence" />
              </BarChart>
            </Card>
          </Col>
        </Row>
      </div>
    );
  };

  // Pour le rendu détaillé avec tous les éléments de l'objet
  const renderDetailedTable = () => {
    // Définition des colonnes pour l'affichage détaillé
    const detailedColumns = [
      ...columns.slice(0, -1), // Toutes les colonnes sauf "Actions"
      {
        title: 'Colonnes',
        dataIndex: 'colonnes',
        key: 'colonnes',
        render: (colonnes) => (
          <div className="flex flex-wrap gap-1">
            {colonnes && colonnes.map((col, index) => (
              <Tag key={index} color="blue">{col}</Tag>
            ))}
          </div>
        ),
      },
      {
        title: 'Manquants',
        dataIndex: 'manquants',
        key: 'manquants',
        render: renderManquants,
      },
      {
        title: 'Position',
        dataIndex: 'position',
        key: 'position',
        render: (position) => position !== null ? position : 'N/A',
      },
      {
        title: 'Infos Détaillées',
        dataIndex: 'infos',
        key: 'infos',
        render: (infos) => (
          <Button 
            type="link" 
            onClick={(e) => {
              e.stopPropagation();
              // Afficher un modal avec les informations détaillées
            }}
          >
            Voir les détails ({infos?.length || 0} éléments)
          </Button>
        ),
      },
    ];

    return (
      <Table
        columns={detailedColumns}
        dataSource={data}
        rowKey={(record, index) => index}
        pagination={false}
        className={darkMode ? 'table-dark' : ''}
        expandable={{
          expandedRowRender: record => (
            <div>
              <h4>Informations détaillées</h4>
              {renderInfoDetails(record.infos)}
            </div>
          ),
        }}
      />
    );
  };

  // Rendu principal
  return (
    <div className={`p-4 ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-100'}`}>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Tableau de Bord Loterie</h1>
        <Space>
          <Input
            placeholder="Rechercher..."
            prefix={<SearchOutlined />}
            onChange={e => setSearchText(e.target.value)}
            onPressEnter={fetchData}
            style={{ width: 200 }}
          />
          <Button 
            type="primary" 
            icon={<RefreshCw size={16} />}
            onClick={fetchData}
          >
            Actualiser
          </Button>
          <Tooltip title={darkMode ? "Mode clair" : "Mode sombre"}>
            <Button 
              icon={darkMode ? <Sun size={16} /> : <Moon size={16} />} 
              onClick={toggleTheme}
            />
          </Tooltip>
        </Space>
      </div>
      
      <div className="flex flex-wrap gap-4 mb-4">
        <Card className={`stats-card ${darkMode ? 'bg-gray-800 text-white' : ''}`}>
          <Statistic
            title="Total Suites"
            value={stats.totalSuites}
            valueStyle={{ color: '#3f8600' }}
          />
        </Card>
        <Card className={`stats-card ${darkMode ? 'bg-gray-800 text-white' : ''}`}>
          <Statistic
            title="Suites Complètes"
            value={stats.completesSuites}
            suffix={`/ ${stats.totalSuites}`}
            valueStyle={{ color: '#cf1322' }}
          />
        </Card>
      </div>
      
      <Card className={`mb-4 ${darkMode ? 'bg-gray-800 text-white' : ''}`}>
        <div className="flex flex-wrap gap-4 mb-4">
          <div>
            <label className="block mb-1">Type de Suite</label>
            <Select
              mode="multiple"
              style={{ width: 220 }}
              placeholder="Sélectionner type"
              value={filters.typeSuite}
              onChange={(value) => handleFilterChange('typeSuite', value)}
            >
              <Option value="arithmetique">Arithmétique</Option>
              <Option value="geometrique">Géométrique</Option>
              <Option value="premiers">Premiers</Option>
            </Select>
          </div>
          
          <div>
            <label className="block mb-1">Type de Tirage</label>
            <Select
              mode="multiple"
              style={{ width: 180 }}
              placeholder="Sélectionner tirage"
              value={filters.typeTirage}
              onChange={(value) => handleFilterChange('typeTirage', value)}
            >
              <Option value="Reveil">Réveil</Option>
              <Option value="Sika">Sika</Option>
            </Select>
          </div>
          
          <div>
            <label className="block mb-1">Sens d'Analyse</label>
            <Select
              style={{ width: 180 }}
              placeholder="Sélectionner sens"
              value={filters.sens}
              onChange={(value) => handleFilterChange('sens', value)}
            >
              <Option value="horizontal">Horizontal</Option>
              <Option value="vertical">Vertical</Option>
              <Option value="les_deux">Les deux</Option>
            </Select>
          </div>
          
          <div>
            <label className="block mb-1">Ordre</label>
            <Radio.Group 
              value={sortOrder} 
              onChange={(e) => setSortOrder(e.target.value)}
              buttonStyle="solid"
            >
              <Radio.Button value="croissant">
                <SortAsc size={16} className="mr-1" />
                Croissant
              </Radio.Button>
              <Radio.Button value="decroissant">
                <SortDesc size={16} className="mr-1" />
                Décroissant
              </Radio.Button>
            </Radio.Group>
          </div>
          
          <div>
            <label className="block mb-1">Nombre min. d'éléments</label>
            <Input
              type="number"
              style={{ width: 100 }}
              value={filters.minElements}
              onChange={(e) => handleFilterChange('minElements', parseInt(e.target.value))}
              min={3}
              max={10}
            />
          </div>
        </div>
        
        <div className="flex flex-wrap gap-4 mb-4">
          <div>
            <Switch 
              checked={filters.forcerMin} 
              onChange={(checked) => handleFilterChange('forcerMin', checked)} 
            /> 
            <span className="ml-2">Forcer min</span>
          </div>
          
          <div>
            <Switch 
              checked={filters.verifierCompletion} 
              onChange={(checked) => handleFilterChange('verifierCompletion', checked)} 
            /> 
            <span className="ml-2">Vérifier complétion</span>
          </div>
          
          <div>
            <Switch 
              checked={filters.respecterPosition} 
              onChange={(checked) => handleFilterChange('respecterPosition', checked)} 
            /> 
            <span className="ml-2">Respecter position</span>
          </div>
        </div>
        
        <div className="flex justify-between items-center">
          <Space>
            <Segmented
              value={viewMode}
              onChange={setViewMode}
              options={[
                {
                  label: (
                    <div className="flex items-center">
                      <TableIcon size={16} className="mr-1" />
                      <span>Tableau</span>
                    </div>
                  ),
                  value: 'table',
                },
                {
                  label: (
                    <div className="flex items-center">
                      <BarChart2 size={16} className="mr-1" />
                      <span>Graphiques</span>
                    </div>
                  ),
                  value: 'chart',
                },
                {
                  label: (
                    <div className="flex items-center">
                      <LineChartIcon size={16} className="mr-1" />
                      <span>Cartes</span>
                    </div>
                  ),
                  value: 'card',
                },
                {
                  label: (
                    <div className="flex items-center">
                      <InfoCircleOutlined style={{ marginRight: '4px' }} />
                      <span>Détaillé</span>
                    </div>
                  ),
                  value: 'detailed',
                },
              ]}
            />
          </Space>
          
          <Tooltip title="Exporter les données">
            <Button icon={<DownloadOutlined />}>
              Exporter
            </Button>
          </Tooltip>
        </div>
      </Card>
      
      <div className="mb-4">
        {loading ? (
          <div className="flex justify-center items-center p-8">
            <Spin size="large" />
          </div>
        ) : (
          <>
            {viewMode === 'table' && (
              <div className={`${darkMode ? 'ant-table-dark' : ''}`}>
                <Table
                  columns={columns}
                  dataSource={data}
                  rowKey={(record, index) => index}
                  pagination={false}
                  className={darkMode ? 'table-dark' : ''}
                />
              </div>
            )}
            
            {viewMode === 'chart' && renderChartView()}
            
            {viewMode === 'card' && renderCardView()}
            
            {viewMode === 'detailed' && renderDetailedTable()}
          </>
        )}
      </div>
      
      <div className="flex justify-end">
        <Pagination
          current={pagination.current}
          pageSize={pagination.pageSize}
          total={pagination.total}
          onChange={handlePageChange}
          showSizeChanger
          showQuickJumper
          showTotal={(total) => `Total ${total} items`}
        />
      </div>
    </div>
  );
};

export default LotteryDashboard;