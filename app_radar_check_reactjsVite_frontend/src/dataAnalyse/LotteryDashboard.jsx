import React, { useState, useEffect } from "react";
import {
  Container,
  Header,
  Content,
  Footer,
  Nav,
  Panel,
  PanelGroup,
  Placeholder,
  DateRangePicker,
  Button,
  InputNumber,
  Form,
  SelectPicker,
  Pagination,
  Badge,
  TagGroup,
  Tag,
  Table,
  Loader,
  Modal,
  ButtonToolbar,
  IconButton,
  Dropdown,
  Message,
  Notification,
  Checkbox,
  FlexboxGrid,
} from "rsuite";
import axios from "axios";
import {
  Search,
  Plus,
  Filter,
  RotateCcw,
  Download,
  Calendar,
  ChevronRight,
  ChevronDown,
  ArrowRight,
  BarChart,
  PieChart,
  TableIcon,
} from "lucide-react";

// Définition des colonnes pour les tableaux des différentes tailles de groupes
// Modifiez l'implémentation du dropdown dans getColumns
const getColumns = (size) => {
    const baseColumns = [
      {
        key: "numbers",
        label: "Numéros",
        width: 180,
        flexGrow: 1,
        cell: (rowData) => (
          <TagGroup>
            {rowData.numbers.map((number, i) => (
              <Tag key={i} color="blue" className="rounded-full">
                {number}
              </Tag>
            ))}
          </TagGroup>
        ),
      },
      {
        key: "count",
        label: "Occurrences",
        width: 100,
        flexGrow: 1,
        cell: (rowData) => <Badge content={rowData.count} color="violet" />,
      },
      {
        key: "occurrences",
        label: "Détails",
        width: 180,
        flexGrow: 2,
        cell: (rowData) => {
          const [showModal, setShowModal] = useState(false);
          
          return (
            <>
              <Button 
                appearance="subtle" 
                size="sm" 
                onClick={() => setShowModal(true)}
              >
                Détails <ChevronDown size={14} />
              </Button>
              
              <Modal open={showModal} onClose={() => setShowModal(false)} size="xs">
                <Modal.Header>
                  <Modal.Title>Détails des occurrences</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                    {rowData.occurrences.map((occ, i) => (
                      <div key={i} className="p-2 border-b">
                        <small>{occ.date} - {occ.tirage_type}</small>
                      </div>
                    ))}
                  </div>
                </Modal.Body>
                <Modal.Footer>
                  <Button onClick={() => setShowModal(false)} appearance="primary">
                    Fermer
                  </Button>
                </Modal.Footer>
              </Modal>
            </>
          );
        },
      },
    ];
  
    return baseColumns;
  };

// Composant principal
const LotteryDashboard = () => {
  // États pour les données et les filtres
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("size_2");
  const [filters, setFilters] = useState({
    file_path: "./uploads/formatted_lottery_results.csv",
    action: "patterns",
    start_date: "01/01/2020",
    end_date: "31/05/2021",
    search_mode: "both",
    respect_positions: "false",
    group_sizes: [2, 3, 4, 5],
    pagination: "true",
    items_per_page: 10,
    page: 1,
  });

  // Options pour les types de tirage
  const tirageTypes = [
    "Reveil",
    "Etoile",
    "Benediction",
    "Premiere Heure",
    "Emergence",
    "Soutra",
    "Monni",
    "Akwaba",
    "Moaye",
    "Diamant",
    "Espoir",
    "Prestige",
    "Kado",
    "Fortune",
    "Solution",
    "Cash",
    "Baraka",
    "Wari",
    "Privilege",
    "Sika",
    "La Matinale",
    "Day Off",
    "Awale",
  ];

  // Appel API pour récupérer les données
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.post(
        "http://127.0.0.1:5002/allSimilarDrawsAndCombinationFinder",
        filters
      );
      setData(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Erreur lors de la récupération des données:", error);
      Notification.error({
        title: "Erreur",
        description: "Impossible de récupérer les données. Veuillez réessayer.",
      });
      setLoading(false);
    }
  };

  // Charger les données au montage du composant
  useEffect(() => {
    fetchData();
  }, []);

  // Mise à jour des filtres
  const handleFilterChange = (name, value) => {
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Soumission du formulaire de filtres
  const handleSubmit = () => {
    fetchData();
  };

  // Affichage d'un tableau spécifique selon la taille du groupe
  const renderTable = (size) => {
    if (!data.groups || !data.groups[`size_${size}`])
      return <Placeholder.Paragraph rows={5} />;

    const groupData = data.groups[`size_${size}`];
    const columns = getColumns(size);

    return (
      <Table
        height={400}
        data={groupData.patterns}
        rowHeight={60}
        hover={true}
        autoHeight={false}
        bordered
        cellBordered
        wordWrap
        style={{ overflow: "visible" }} // Add this line to allow content to overflow
      >
        {columns.map((column) => (
          <Table.Column
            flexGrow={column.flexGrow}
            width={column.width}
            key={column.key}
          >
            <Table.HeaderCell>{column.label}</Table.HeaderCell>
            <Table.Cell>{column.cell}</Table.Cell>
          </Table.Column>
        ))}
      </Table>
    );
  };

  // Rendu du composant
  return (
    <Container className="h-screen">
      <Header className="bg-blue-900 text-white p-4">
        <FlexboxGrid justify="space-between" align="middle">
          <FlexboxGrid.Item>
            <h1 className="text-2xl font-bold">Tableau de Bord Lotterie</h1>
          </FlexboxGrid.Item>
          <FlexboxGrid.Item>
            <ButtonToolbar>
              <Button appearance="ghost" className="text-white">
                <RotateCcw size={16} className="mr-1" /> Actualiser
              </Button>
              <Button appearance="primary">
                <Download size={16} className="mr-1" /> Exporter
              </Button>
            </ButtonToolbar>
          </FlexboxGrid.Item>
        </FlexboxGrid>
      </Header>

      <Content className="bg-gray-50 p-4">
        <FlexboxGrid>
          <FlexboxGrid.Item colspan={24}>
            <Panel
              className="shadow-md bg-white"
              header={
                <h3 className="flex items-center">
                  <Filter size={16} className="mr-2" /> Filtres avancés
                </h3>
              }
              bordered
              collapsible
            >
              <Form layout="inline" fluid>
                <Form.Group>
                  <Form.ControlLabel>Période</Form.ControlLabel>
                  <DateRangePicker
                    format="DD/MM/YYYY"
                    value={[
                      new Date(
                        filters.start_date.split("/").reverse().join("-")
                      ),
                      new Date(filters.end_date.split("/").reverse().join("-")),
                    ]}
                    onChange={(value) => {
                      if (value && value.length === 2) {
                        const formatDate = (date) => {
                          const day = date
                            .getDate()
                            .toString()
                            .padStart(2, "0");
                          const month = (date.getMonth() + 1)
                            .toString()
                            .padStart(2, "0");
                          const year = date.getFullYear();
                          return `${day}/${month}/${year}`;
                        };
                        handleFilterChange("start_date", formatDate(value[0]));
                        handleFilterChange("end_date", formatDate(value[1]));
                      }
                    }}
                  />
                </Form.Group>

                <Form.Group>
                  <Form.ControlLabel>Types de tirage</Form.ControlLabel>
                  <SelectPicker
                    data={tirageTypes.map((type) => ({
                      label: type,
                      value: type,
                    }))}
                    value={filters.tirage_types}
                    onChange={(value) =>
                      handleFilterChange("tirage_types", value || [])
                    }
                    cleanable
                    searchable
                    multiple
                    placeholder="Sélectionnez"
                  />
                </Form.Group>

                <Form.Group>
                  <Form.ControlLabel>Tailles des groupes</Form.ControlLabel>
                  <SelectPicker
                    data={[1, 2, 3, 4, 5].map((size) => ({
                      label: `${size} numéro(s)`,
                      value: size,
                    }))}
                    value={filters.group_sizes}
                    onChange={(value) =>
                      handleFilterChange(
                        "group_sizes",
                        value || [1, 2, 3, 4, 5]
                      )
                    }
                    cleanable
                    searchable
                    multiple
                    placeholder="Sélectionnez"
                  />
                </Form.Group>

                <Form.Group>
                  <Form.ControlLabel>Éléments par page</Form.ControlLabel>
                  <InputNumber
                    min={5}
                    max={100}
                    value={filters.items_per_page}
                    onChange={(value) =>
                      handleFilterChange("items_per_page", value)
                    }
                  />
                </Form.Group>

                <Form.Group>
                  <Form.ControlLabel>Respect des positions</Form.ControlLabel>
                  <Checkbox
                    checked={filters.respect_positions}
                    onChange={(_, checked) =>
                      handleFilterChange("respect_positions", checked)
                    }
                  />
                </Form.Group>

                <Form.Group>
                  <Button appearance="primary" onClick={handleSubmit}>
                    <Search size={16} className="mr-1" /> Rechercher
                  </Button>
                </Form.Group>
              </Form>
            </Panel>
          </FlexboxGrid.Item>
        </FlexboxGrid>

        <div className="mt-4">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <Loader size="lg" content="Chargement des données..." />
            </div>
          ) : (
            <>

              {/* Onglets pour les différentes tailles de groupes */}
              <Nav
                appearance="tabs"
                activeKey={activeTab}
                onSelect={setActiveTab}
                className="mb-4"
              >
                {[2, 3, 4, 5].map((size) => (
                  <Nav.Item key={`size_${size}`} eventKey={`size_${size}`}>
                    Groupes de {size} numéros
                    {data.groups && data.groups[`size_${size}`] && (
                      <Badge
                        content={data.groups[`size_${size}`].total_patterns}
                        color="blue"
                      />
                    )}
                  </Nav.Item>
                ))}
              </Nav>

              {/* Tableau des données selon l'onglet actif */}
              <Panel className="shadow-md bg-white" bordered bodyFill>
                {activeTab && renderTable(activeTab.split("_")[1])}
              </Panel>
            </>
          )}
        </div>
      </Content>

      <Footer className="p-4 text-center text-gray-600">
        <p>&copy; 2025 Lottery Dashboard - Tous droits réservés</p>
      </Footer>
    </Container>
  );
};

export default LotteryDashboard;
