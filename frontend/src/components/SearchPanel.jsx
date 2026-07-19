import React from "react";

export default function SearchPanel({ searchQuery, setSearchQuery, onSearch, searchResults }) {
  return (
    <section className="panel search-panel">
      <div className="panel-header">
        <h2>Search</h2>
        <span>Semantic retrieval</span>
      </div>
      <form onSubmit={onSearch} className="search-row">
        <input
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
          placeholder="Search uploaded documents"
          aria-label="Search uploaded documents"
        />
        <button className="primary" type="submit">Search</button>
      </form>
      {searchResults.length === 0 ? (
        <div className="empty-state">Run a search to see matching chunks with their relevance scores.</div>
      ) : (
        <div className="search-results">
          {searchResults.map((chunk) => (
            <article key={chunk.chunk_id}>
              <strong>{chunk.filename}</strong>
              <span>
                Chunk {chunk.chunk_index} · score {Number(chunk.score).toFixed(3)}
              </span>
              <p>{chunk.chunk_text}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
