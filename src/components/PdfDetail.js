import React from 'react';

const PdfDetail = ({ pdf }) => {
  return (
    <div className="pdf-detail">
      <h2>Book Name: {pdf.name}</h2>
      <h3>By: {pdf.author}</h3>
      <p><strong>Link:</strong> <a href={pdf.link} target="_blank" rel="noopener noreferrer">Read PDF</a></p>
      <p><strong>Published:</strong> {pdf.published}</p>
    </div>
  );
};

export default PdfDetail;
