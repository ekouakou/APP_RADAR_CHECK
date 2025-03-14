// App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Container, 
  Typography, 
  Box, 
  CircularProgress, 
  Pagination, 
  Paper, 
  Accordion, 
  AccordionSummary,
  AccordionDetails,
  Chip,
  Grid, 
  Card, 
  CardContent,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import HorizontalRuleIcon from '@mui/icons-material/HorizontalRule';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

// Configuration de base pour Axios
const API_URL = 'http://127.0.0.1:5000/api/suites/analyser';

function formatDate(dateStr) {
  return dateStr;
}

function Dashborad() {
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
    date_debut: "01/01/2020",
    date_fin: "26/12/2021",
    ordre: "decroissant",
    min_elements: 4,
    forcer_min: true,
    verifier_completion: true,
    respecter_position: false,
    source_numeros: "tous",
    ordre_lecture: "normal",
    types_tirage: ["Reveil"],
    sens_analyse: "bidirectionnel",
    pagination: true,
    items_par_page: itemsPerPage,
    page: currentPage
  };

  // Fonction pour récupérer les données
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.post(API_URL, {
        ...requestConfig,
        page: currentPage
      });
      
      setData(response.data);
      setTotalPages(response.data.total_pages);
      setLoading(false);
    } catch (err) {
      setError('Erreur lors de la récupération des données: ' + err.message);
      setLoading(false);
    }
  };

  // Chargement initial des données
  useEffect(() => {
    fetchData();
  }, [currentPage]); // Recharger lors du changement de page

  // Gestionnaire de changement de page
  const handlePageChange = (event, value) => {
    setCurrentPage(value);
  };

  // Fonction pour afficher les nombres manquants
  const renderManquants = (manquants) => {
    if (!manquants || manquants.length === 0) return <Chip label="Aucun" color="success" size="small" />;
    
    if (manquants.length > 10) {
      return (
        <Tooltip title={manquants.join(', ')} arrow>
          <Chip 
            label={`${manquants.length} nombres`} 
            color="warning" 
            size="small" 
            icon={<InfoIcon />} 
          />
        </Tooltip>
      );
    }
    
    return manquants.map((num, index) => (
      <Chip 
        key={index} 
        label={num} 
        color="warning" 
        size="small" 
        style={{ margin: '2px' }} 
      />
    ));
  };

  // Fonction pour afficher la suite
  const renderSuite = (suite) => {
    return suite.map((num, index) => (
      <Chip 
        key={index} 
        label={num} 
        color="primary" 
        size="small" 
        style={{ margin: '2px' }} 
      />
    ));
  };

  // Rendu des détails d'une suite avec informations supplémentaires
  const renderInfosSuite = (infos) => {
    if (!infos) return null;
    
    return (
      <TableContainer component={Paper} variant="outlined" style={{ marginTop: '15px' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Numéro</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Type tirage</TableCell>
              <TableCell>Position</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {infos.map((info, index) => (
              <TableRow key={index}>
                <TableCell>{info[0]}</TableCell>
                <TableCell>{info[1]}</TableCell>
                <TableCell>{info[2]}</TableCell>
                <TableCell>{info[3]}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  // Icône pour le sens
  const getSensIcon = (sens) => {
    if (sens === "horizontal") return <HorizontalRuleIcon />;
    if (sens === "vertical") return <ArrowDownwardIcon />;
    return null;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
        Tableau de Bord d'Analyse de Suites
      </Typography>
      
      {data && (
        <>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="subtitle1">
              Page {data.page_courante} sur {data.total_pages} • 
              Total de résultats: {data.total_resultats}
            </Typography>
            <Pagination 
              count={data.total_pages} 
              page={currentPage}
              onChange={handlePageChange}
              color="primary"
              showFirstButton
              showLastButton
            />
          </Box>

          {data.resultats.map((resultat, index) => (
            <Accordion key={index} sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Grid container alignItems="center" spacing={2}>
                  <Grid item>
                    <Typography variant="body1" fontWeight="bold">
                      Suite {index + 1 + (currentPage - 1) * itemsPerPage}
                    </Typography>
                  </Grid>
                  <Grid item>
                    <Chip 
                      label={resultat.type_suite}
                      color={resultat.type_suite === "arithmetique" ? "primary" : 
                             resultat.type_suite === "premiers" ? "secondary" : "default"}
                      size="small"
                    />
                  </Grid>
                  <Grid item>
                    <Tooltip title={`Sens: ${resultat.sens}`}>
                      <IconButton size="small">
                        {getSensIcon(resultat.sens)}
                      </IconButton>
                    </Tooltip>
                  </Grid>
                  <Grid item>
                    {resultat.complete ? 
                      <Tooltip title="Suite complète">
                        <CheckCircleIcon color="success" fontSize="small" />
                      </Tooltip> : 
                      <Tooltip title="Suite incomplète">
                        <CancelIcon color="error" fontSize="small" />
                      </Tooltip>
                    }
                  </Grid>
                  <Grid item xs>
                    <Typography variant="body2" color="text.secondary">
                      {resultat.date && `Date: ${formatDate(resultat.date)}`} • 
                      Type: {resultat.type_tirage}
                    </Typography>
                  </Grid>
                </Grid>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Éléments de la suite
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                          {renderSuite(resultat.suite)}
                        </Box>
                        
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Nombres manquants:
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {renderManquants(resultat.manquants)}
                          </Box>
                        </Box>
                        
                        <Typography variant="subtitle2" gutterBottom>
                          Raisons:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {resultat.raisons.map((raison, i) => (
                            <Chip 
                              key={i} 
                              label={raison} 
                              color="info" 
                              size="small" 
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Colonnes
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {resultat.colonnes.map((colonne, i) => (
                            <Chip 
                              key={i} 
                              label={colonne} 
                              color="default" 
                              size="small" 
                              variant="outlined"
                            />
                          ))}
                        </Box>
                        
                        {resultat.position && (
                          <Typography variant="body2" sx={{ mt: 2 }}>
                            Position: {resultat.position}
                          </Typography>
                        )}
                        
                        {resultat.infos && renderInfosSuite(resultat.infos)}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}
          
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <Pagination 
              count={data.total_pages} 
              page={currentPage}
              onChange={handlePageChange}
              color="primary"
              showFirstButton
              showLastButton
              size="large"
            />
          </Box>
        </>
      )}
    </Container>
  );
}

export default Dashborad;