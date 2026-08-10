import React from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { setQuery, searchIncidents } from '../store';
import { useDispatch } from 'react-redux';

export default function Search({
  searchQuery,
  searchResults,
  searchLoading,
  onMachineSelect,
  onSearchSubmit,
  onClearSearch
}) {
  const dispatch = useDispatch();
  const quickTags = ["Bearing", "Coolant", "Vibration", "Overheat", "Shaft", "M101", "M102"];
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2>Historical Incident Database Search</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Query historical incident logs indexed in Apache Solr to find similar signatures and verified actions.
        </p>
      </div>

      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <form onSubmit={onSearchSubmit} className="search-container" style={{ maxWidth: '100%' }}>
          <SearchIcon size={16} className="text-secondary" />
          <input
            type="text"
            className="search-input"
            placeholder="Search historical incidents (e.g. bearing, coolant, overheat)..."
            value={searchQuery}
            onChange={(e) => dispatch(setQuery(e.target.value))}
          />
          {searchQuery && (
            <button type="button" onClick={onClearSearch} style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', fontSize: '11px' }}>
              Clear
            </button>
          )}
        </form>

        {/* Quick tags */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Quick Filters:</span>
          {quickTags.map((tag) => (
            <button
              key={tag}
              onClick={() => {
                dispatch(setQuery(tag));
                dispatch(searchIncidents(tag));
              }}
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--border-glass)',
                borderRadius: '6px',
                padding: '4px 10px',
                color: 'var(--text-secondary)',
                fontSize: '11px',
                cursor: 'pointer',
                transition: 'var(--transition-smooth)'
              }}
              onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.08)'}
              onMouseOut={(e) => e.target.style.background = 'rgba(255,255,255,0.03)'}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Results Container */}
      <div className="glass-card">
        <h3 className="card-title">
          Search Results {searchResults ? `(${searchResults.numFound} logs found)` : ''}
        </h3>

        {searchLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><div className="spinner"></div></div>
        ) : searchResults ? (
          <div className="search-results-list">
            {searchResults.docs.length === 0 ? (
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '20px 0' }}>No historical logs match this search query.</p>
            ) : (
              searchResults.docs.map((doc, idx) => (
                <div key={doc.id || idx} className="search-result-item">
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <strong 
                      onClick={() => onMachineSelect(doc.machine_id)}
                      style={{ color: 'var(--primary)', cursor: 'pointer', textDecoration: 'underline' }}
                    >
                      Machine-{doc.machine_id}
                    </strong>
                    <span style={{ color: 'var(--text-muted)' }}>{new Date(doc.date).toLocaleDateString()}</span>
                  </div>
                  <p style={{ fontSize: '12px', marginTop: '6px' }}>
                    <span style={{ color: 'var(--danger)', fontWeight: 500 }}>Signature:</span> {doc.failure_signature}
                  </p>
                  <p style={{ fontSize: '12px', marginTop: '2px' }}>
                    <span style={{ color: 'var(--success)', fontWeight: 500 }}>Corrective Action:</span> {doc.action_taken}
                  </p>
                  <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Outcome: <span style={{ color: doc.outcome === 'Resolved' ? 'var(--success)' : 'var(--warning)' }}>{doc.outcome}</span>
                  </p>
                </div>
              ))
            )}
          </div>
        ) : (
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '20px 0' }}>
            Submit a search query or click on a quick filter to query incident archives.
          </p>
        )}
      </div>
    </div>
  );
}
