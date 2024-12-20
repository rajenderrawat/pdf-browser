// src/components/SearchBar.js
import React from 'react';

const SearchBar = ({ searchQuery, setSearchQuery }) => {
  return (
    <div>
      <input
        type="text"
        placeholder="Search PDFs by title"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)} 
      />
    </div>
  );
};

export default SearchBar;
