import { Routes, Route, Link } from "react-router-dom";
// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'
import AboutPage from "./components/AboutPage";
import Dashboard from "./AppPages/Dashboard";
import MedecinListe from "./AppPages/MedecinListe";

import Index from "./components";

import AppHeader from "./components/AppHeader";
import AppFooter from "./components/AppFooter";
import AppHeroHeader from "./components/AppHeroHeader";
import MenuSideBar from "./components/MenuSideBar";
import HeaderTopbar from "./AppComponents/HeaderTopbar";
import Header from "./AppComponents/Header";
import HomeBanner from "./AppComponents/HomeBanner";

import List from "./AppComponents/List";
import SpecialitySection from "./AppComponents/SpecialitySection";
import DoctorSection from "./AppComponents/DoctorSection";
import ServicesSection from "./AppComponents/ServicesSection";
import Footer from "./AppComponents/Footer";
import ReasonsSection from "./AppComponents/ReasonsSection";
import LotteryAnalysisComponent from "./AppComponents/LotteryAnalysisComponent";

import BookusSection from "./AppComponents/BookusSection";
import SwaggerUIComponent from "./swagger/SwaggerUIComponent";
import SuitesArithmetiquesVisualisation from "./dataAnalyse/SuitesArithmetiquesVisualisation"
import Dashborad from "./dataAnalyse/Dashborad"

function App() {
  // const [count, setCount] = useState(0)

  return (
    <div className="main-wrapper">

      <>
        <main>
          <Routes>
            {/* <Route path="/" element={<SwaggerUIComponent />} /> */}
            <Route path="/medecinliste" element={<SwaggerUIComponent />} />
            <Route path="/medecinliste2" element={<SuitesArithmetiquesVisualisation />} />
            <Route path="/dashborad" element={<Dashborad />} />
          </Routes>
        </main>
      </>


      <HeaderTopbar />

      <Header />

      <HomeBanner />


      {/* <LotteryAnalysisComponent /> */}

      <List />

      <SpecialitySection />

      <DoctorSection />

      <ServicesSection />

      <ReasonsSection />

      <BookusSection />

      <Footer />

      {/* Cursor */}
      <div className="mouse-cursor cursor-outer" />
      <div className="mouse-cursor cursor-inner" />
      {/* /Cursor */}
    </div>

    // <div className="page-wrapper">
    //   <AppHeader />

    //   {/* Main container starts */}
    //   <div className="main-container">
    //     <MenuSideBar />

    //     {/* App container starts */}
    //     <div className="app-container">
    //       <AppHeroHeader />

    //       {/* App body starts */}

    //       <>
    //         <main>
    //           <Routes>
    //             <Route path="/" element={<Dashboard />} />
    //             <Route path="/medecinliste" element={<MedecinListe />} />
    //           </Routes>
    //         </main>
    //       </>

    //       {/* App body ends */}

    //       <AppFooter />
    //     </div>
    //     {/* App container ends */}
    //   </div>
    //   {/* Main container ends */}
    // </div>
  );
}

export default App;
