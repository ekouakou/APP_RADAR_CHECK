// App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Loader,
  Pagination,
  Panel,
  Grid,
  Row,
  Col,
  Table,
  Tag,
  Message,
  Divider,
} from 'rsuite';
import 'rsuite/dist/rsuite.min.css';

// Configuration de base pour Axios
const API_URL = 'http://127.0.0.1:5002/allSuiteFinder';

function formatDate(dateStr) {
  return dateStr;
}

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);

  // Configuration de la requête
  const requestConfig = {
    file_path: "./uploads/formatted_lottery_results.csv",
    types_suites: ["arithmetique", "geometrique", "premiers", "diff_decroissante"],
    date_debut: "01/12/2021",
    date_fin: "02/12/2021",
    ordre: "croissant",
    min_elements: 4,
    forcer_min: true,
    verifier_completion: true,
    respecter_position: false,
    source_numeros: "tous",
    ordre_lecture: "normal",
    //types_tirage: ["Reveil"],
    sens_analyse: "bidirectionnel",
    pagination: true,
    items_par_page: itemsPerPage,
    page: currentPage
  };

  // Fonction pour récupérer les données
  const fetchData = async () => {
    setLoading(true);
    try {
      console.log("Fetching data...");
      const response = await axios.post(API_URL, {
        ...requestConfig,
        page: currentPage
      });
      
      console.log("Data received:", response.data);
      setData(response.data);
      setTotalPages(response.data.total_pages);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError('Erreur lors de la récupération des données: ' + err.message);
      setLoading(false);
    }
  };

  // Chargement initial des données
  useEffect(() => {
    fetchData();
  }, [currentPage]); // Recharger lors du changement de page

  // Gestionnaire de changement de page
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Fonction pour afficher les nombres manquants
  const renderManquants = (manquants) => {
    if (!manquants || manquants.length === 0) return <Tag color="green">Aucun</Tag>;
    
    if (manquants.length > 10) {
      return (
        <Tag color="yellow" style={{ cursor: 'pointer' }}>
          {manquants.length} nombres
        </Tag>
      );
    }
    
    return manquants.map((num, index) => (
      <Tag key={index} color="yellow" style={{ margin: '2px' }}>
        {num}
      </Tag>
    ));
  };

  // Fonction pour afficher la suite
  const renderSuite = (suite) => {
    return suite.map((num, index) => (
      <Tag key={index} color="blue" style={{ margin: '2px' }}>
        {num}
      </Tag>
    ));
  };

  // Rendu des détails d'une suite avec informations supplémentaires
  const renderInfosSuite = (infos) => {
    if (!infos) return null;
    
    return (
      <Table 
        data={infos.map((info, index) => ({
          id: index,
          numero: info[0],
          date: info[1],
          typeTirage: info[2],
          position: info[3]
        }))}
        autoHeight
        bordered
        style={{ marginTop: '15px' }}
      >
        <Table.Column width={100}>
          <Table.HeaderCell>Numéro</Table.HeaderCell>
          <Table.Cell dataKey="numero" />
        </Table.Column>
        <Table.Column width={150}>
          <Table.HeaderCell>Date</Table.HeaderCell>
          <Table.Cell dataKey="date" />
        </Table.Column>
        <Table.Column width={150}>
          <Table.HeaderCell>Type tirage</Table.HeaderCell>
          <Table.Cell dataKey="typeTirage" />
        </Table.Column>
        <Table.Column width={100}>
          <Table.HeaderCell>Position</Table.HeaderCell>
          <Table.Cell dataKey="position" />
        </Table.Column>
      </Table>
    );
  };

  // Définir la couleur du tag pour le type de suite
  const getSuiteColor = (typeSuite) => {
    switch(typeSuite) {
      case 'arithmetique': return 'blue';
      case 'premiers': return 'violet';
      default: return 'cyan';
    }
  };

  // Rendu de l'indicateur de completeness
  const renderCompleteness = (complete) => {
    return complete ? 
      <span style={{ color: 'green' }}>✓</span> : 
      <span style={{ color: 'red' }}>✗</span>;
  };

  // Rendu de l'indicateur de sens
  const renderDirection = (sens) => {
    if (sens === "horizontal") return "―";
    if (sens === "vertical") return "↓";
    return "";
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Loader size="lg" content="Chargement..." />
      </div>
    );
  }

  if (error) {
    return (
      <Container>
        <Message type="error" showIcon>
          {error}
        </Message>
      </Container>
    );
  }

  return (
    <Container style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '30px', fontWeight: 'bold' }}>
        Tableau de Bord d'Analyse de Suites
      </h1>
      
      {data && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <span>
              Page {data.page_courante} sur {data.total_pages} • 
              Total de résultats: {data.total_resultats}
            </span>
            <Pagination
              prev
              next
              first
              last
              ellipsis
              boundaryLinks
              maxButtons={5}
              size="md"
              total={data.total_resultats}
              limit={itemsPerPage}
              activePage={currentPage}
              onChangePage={handlePageChange}
            />
          </div>

          {data.resultats && data.resultats.map((resultat, index) => (
            <Panel key={index} header={
              <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <div style={{ flex: '0 0 auto', marginRight: '10px' }}>
                  <strong>Suite {index + 1 + (currentPage - 1) * itemsPerPage}</strong>
                </div>
                <div style={{ flex: '0 0 auto', marginRight: '10px' }}>
                  <Tag color={getSuiteColor(resultat.type_suite)}>
                    {resultat.type_suite}
                  </Tag>
                </div>
                <div style={{ flex: '0 0 auto', marginRight: '10px' }}>
                  {renderDirection(resultat.sens)}
                </div>
                <div style={{ flex: '0 0 auto', marginRight: '10px' }}>
                  {renderCompleteness(resultat.complete)}
                </div>
                <div style={{ flex: '1 1 auto', color: '#999' }}>
                  {resultat.date && `Date: ${formatDate(resultat.date)}`} • 
                  Type: {resultat.type_tirage}
                </div>
              </div>
            } collapsible bordered style={{ marginBottom: '10px' }}>
              <Grid fluid>
                <Row>
                  <Col xs={24} md={12}>
                    <Panel bordered>
                      <h5>Éléments de la suite</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginBottom: '15px' }}>
                        {renderSuite(resultat.suite)}
                      </div>
                      
                      <div style={{ marginBottom: '15px' }}>
                        <h6>Nombres manquants:</h6>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                          {renderManquants(resultat.manquants)}
                        </div>
                      </div>
                      
                      <h6>Raisons:</h6>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                        {resultat.raisons && resultat.raisons.map((raison, i) => (
                          <Tag key={i} color="cyan" style={{ margin: '2px' }}>
                            {raison}
                          </Tag>
                        ))}
                      </div>
                    </Panel>
                  </Col>
                  <Col xs={24} md={12}>
                    <Panel bordered>
                      <h5>Colonnes</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                        {resultat.colonnes && resultat.colonnes.map((colonne, i) => (
                          <Tag key={i} color="gray" style={{ margin: '2px' }}>
                            {colonne}
                          </Tag>
                        ))}
                      </div>
                      
                      {resultat.position && (
                        <div style={{ marginTop: '15px' }}>
                          Position: {resultat.position}
                        </div>
                      )}
                      
                      {resultat.infos && renderInfosSuite(resultat.infos)}
                    </Panel>
                  </Col>
                </Row>
              </Grid>
            </Panel>
          ))}
          
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '30px' }}>
            <Pagination
              prev
              next
              first
              last
              ellipsis
              boundaryLinks
              maxButtons={5}
              size="lg"
              total={data.total_resultats}
              limit={itemsPerPage}
              activePage={currentPage}
              onChangePage={handlePageChange}
            />
          </div>
        </>
      )}
    </Container>
  );
}

export default Dashboard;