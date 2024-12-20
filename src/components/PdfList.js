import React from "react";

const PdfList = ({ pdfs, onPdfSelect }) => {
  return (
    <div className="pdf-list">
      {pdfs.map((pdf) => (
        <div
          key={pdf.id}
          className="pdf-item"
          onClick={() => onPdfSelect(pdf)}
        >
          <div className="pdf-info">
            <h3>{pdf.name}</h3>
            <p>{pdf.author ? pdf.author : "Unknown Author"}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PdfList;
