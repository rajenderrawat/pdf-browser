// src/App.js
import React, { useState, useEffect } from "react";
import PdfList from "./components/PdfList";
import PdfDetail from "./components/PdfDetail";
import "./App.css";

const App = () => {
  const [pdfs, setPdfs] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPdf, setSelectedPdf] = useState(null);

  useEffect(() => {
    fetch("https://api.npoint.io/dee51ea017d20efdfcc8")
      .then((response) => response.json())
      .then((data) => setPdfs(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handlePdfSelect = (pdf) => {
    setSelectedPdf(pdf);
  };

  const filteredPdfs = pdfs.filter(
    (pdf) =>
      (pdf.name && pdf.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (pdf.author && pdf.author.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">PDF Library</h1>
        <input
          type="text"
          className="search-bar"
          placeholder="Search by name or author..."
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </header>

      <div className="content">
        {selectedPdf ? (
          <PdfDetail pdf={selectedPdf} />
        ) : (
          <PdfList pdfs={filteredPdfs} onPdfSelect={handlePdfSelect} />
        )}
      </div>
    </div>
  );
};

export default App;
