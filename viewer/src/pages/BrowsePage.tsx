import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getCatalog, getAssetUrl } from '../api/client';

type BrowsePageProps = {
  sectionName: string;
  title: string;
};

export const BrowsePage: React.FC<BrowsePageProps> = ({
  sectionName,
  title,
}) => {
  const [shows, setShows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');

    getCatalog()
      .then((catalogue) => {
        const section = catalogue.sections?.find(
          (item: any) =>
            item.name?.toLowerCase() === sectionName.toLowerCase(),
        );

        setShows(section?.shows || []);
      })
      .catch(() =>
        setError('Catalogue could not be loaded. Please try again later.'),
      )
      .finally(() => setLoading(false));
  }, [sectionName]);

  return (
    <main className="browse-page">
      <h1 className="browse-title">{title}</h1>

      {loading ? (
        <div className="browse-state">Loading...</div>
      ) : error ? (
        <div className="browse-state">{error}</div>
      ) : shows.length === 0 ? (
        <div className="browse-state">
          No {title.toLowerCase()} are currently published.
        </div>
      ) : (
        <div className="browse-grid">
          {shows.map((show) => (
            <Link
              key={show.id}
              to={`/title/${show.slug || show.id}`}
              className="poster-card"
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
    </main>
  );
};