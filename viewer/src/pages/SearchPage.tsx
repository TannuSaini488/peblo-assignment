import React, { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { searchCatalog, getAssetUrl } from '../api/client';

const CATEGORIES = [
  'adventure',
  'folk',
  'friendship',
  'india',
  'language',
  'learning',
  'maths',
  'music',
  'nature',
  'reading',
  'science',
  'singalong',
  'stories',
  'travel',
  'values',
];

const LANGUAGES = ['en', 'hi'];

export const SearchPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || '';
  const language = searchParams.get('language') || '';

  const [draftQuery, setDraftQuery] = useState(query);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setDraftQuery(query);
  }, [query]);

  useEffect(() => {
    setLoading(true);

    searchCatalog({
      q: query || undefined,
      category: category || undefined,
      language: language || undefined,
    })
      .then(data => {
        setResults(data.results || []);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [query, category, language]);

  const updateParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);

    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }

    navigate(`/search?${params.toString()}`);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    updateParam('q', draftQuery.trim());
  };

  const hasFilters = Boolean(query || category || language);

  return (
    <div className="search-page">
      <h2 className="search-heading">
        {hasFilters ? 'Search results' : 'Browse catalogue'}
      </h2>

      <form className="viewer-filter-bar" onSubmit={handleSubmit}>
        <input
          value={draftQuery}
          onChange={(event) => setDraftQuery(event.target.value)}
          placeholder="Search titles, episodes, categories"
        />

        <select
          value={category}
          onChange={(event) =>
            updateParam('category', event.target.value)
          }
        >
          <option value="">All categories</option>

          {CATEGORIES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <select
          value={language}
          onChange={(event) =>
            updateParam('language', event.target.value)
          }
        >
          <option value="">All languages</option>

          {LANGUAGES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <button className="btn btn-play" type="submit">
          Search
        </button>
      </form>

      {loading ? (
        <div className="search-state">Searching...</div>
      ) : results.length === 0 ? (
        <div className="search-state">
          <h3>No titles found</h3>

          <p style={{ marginTop: '16px' }}>
            Try a different search or remove a filter.
          </p>
        </div>
      ) : (
        <div className="search-grid">
          {results.map((show: any) => (
            <Link
              key={show.id}
              to={`/title/${show.slug || show.id}`}
              className="poster-card"
              style={{ display: 'block' }}
            >
              {show.artwork?.poster ? (
                <img
                  src={getAssetUrl(show.artwork.poster)}
                  alt={show.title}
                  loading="lazy"
                />
              ) : (
                <div
                  className="image-skeleton"
                  style={{
                    width: '100%',
                    aspectRatio: '2/3',
                  }}
                />
              )}

              <span className="poster-title">{show.title}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};