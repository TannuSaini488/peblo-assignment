import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getCatalog, getAssetUrl } from '../api/client';
import { Play, Info } from 'lucide-react';

export const Home: React.FC = () => {
  const [catalogue, setCatalogue] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCatalog()
      .then(data => setCatalogue(data))
      .catch(err => console.error('Failed to load catalog', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center" style={{ marginTop: '100px' }}>
        Loading...
      </div>
    );
  }

  if (!catalogue || !catalogue.sections) {
    return (
      <div className="p-8 text-center" style={{ marginTop: '100px' }}>
        Catalogue not available
      </div>
    );
  }

  const firstSection = catalogue.sections[0];
  const heroShow = firstSection?.shows?.[0];

  return (
    <div>
      {heroShow && (
        <div
          className="hero"
          style={{
            backgroundImage: `url(${getAssetUrl(heroShow.artwork?.banner)})`,
          }}
        >
          <div className="hero-gradient"></div>

          <div className="hero-content">
            <h1 className="hero-title">{heroShow.title}</h1>

            <p className="hero-synopsis">{heroShow.synopsis}</p>

            <div style={{ display: 'flex', gap: '16px' }}>
              <button className="btn btn-play">
                <Play fill="black" size={24} /> Play
              </button>

              <Link
                to={`/title/${heroShow.slug || heroShow.id}`}
                className="btn btn-info"
              >
                <Info size={24} /> More Info
              </Link>
            </div>
          </div>
        </div>
      )}

      <div
        style={{
          marginTop: '-10vh',
          position: 'relative',
          zIndex: 10,
        }}
      >
        {catalogue.sections.map((section: any, i: number) => (
          <div key={i} className="row">
            <h2 className="row-title">{section.name}</h2>

            <div className="row-posters">
              {section.shows.map((show: any) => (
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
                    ></div>
                  )}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div style={{ height: '100px' }}></div>
    </div>
  );
};