import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getCatalog, getAssetUrl } from '../api/client';
import { Play } from 'lucide-react';

export const ShowDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [show, setShow] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCatalog()
      .then(data => {
        let found = null;

        for (const section of data.sections) {
          found = section.shows.find(
            (s: any) => s.id === id || s.slug === id,
          );

          if (found) break;
        }

        setShow(found);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div
        className="p-8 text-center"
        style={{ marginTop: '100px' }}
      >
        Loading...
      </div>
    );
  }

  if (!show) {
    return (
      <div
        className="p-8 text-center"
        style={{ marginTop: '100px' }}
      >
        Show not found
      </div>
    );
  }

  return (
    <div>
      {/* Hero */}
      <div
        className="hero"
        style={{
          backgroundImage: `url(${getAssetUrl(
            show.artwork?.banner,
          )})`,
          height: '60vh',
        }}
      >
        <div className="hero-gradient"></div>

        <div className="hero-content">
          <h1 className="hero-title">{show.title}</h1>

          <div
            style={{
              display: 'flex',
              gap: '8px',
              marginBottom: '16px',
            }}
          >
            {show.categories?.map((cat: string, i: number) => (
              <span
                key={i}
                style={{ color: 'var(--text-muted)' }}
              >
                {cat}
                {i < show.categories.length - 1 ? ' •' : ''}
              </span>
            ))}
          </div>

          <p className="hero-synopsis">{show.synopsis}</p>
        </div>
      </div>

      <div
        className="row"
        style={{
          marginTop: '-5vh',
          position: 'relative',
          zIndex: 10,
        }}
      >
        {/* Trailers */}
        {show.trailers?.length > 0 && (
          <div style={{ marginBottom: '32px' }}>
            <h2>Trailers</h2>

            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                marginTop: '16px',
              }}
            >
              {show.trailers.map((trailer: any, i: number) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    gap: '24px',
                    padding: '16px',
                    backgroundColor: 'var(--bg-card)',
                    borderRadius: '8px',
                    alignItems: 'center',
                  }}
                >
                  <div
                    style={{
                      flex: '0 0 160px',
                      position: 'relative',
                    }}
                  >
                    {trailer.artwork?.thumbnail ? (
                      <img
                        src={getAssetUrl(
                          trailer.artwork.thumbnail,
                        )}
                        alt={trailer.title}
                        style={{
                          width: '100%',
                          borderRadius: '4px',
                        }}
                      />
                    ) : (
                      <div
                        className="image-skeleton"
                        style={{
                          width: '100%',
                          aspectRatio: '16/9',
                        }}
                      ></div>
                    )}

                    <div
                      style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform:
                          'translate(-50%, -50%)',
                      }}
                    >
                      <div
                        style={{
                          backgroundColor:
                            'rgba(0,0,0,0.5)',
                          borderRadius: '50%',
                          padding: '8px',
                        }}
                      >
                        <Play fill="white" size={24} />
                      </div>
                    </div>
                  </div>

                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                      }}
                    >
                      <h4
                        style={{
                          fontSize: '1.1rem',
                          marginBottom: '8px',
                        }}
                      >
                        {trailer.title}
                      </h4>

                      <span
                        style={{
                          color: 'var(--text-muted)',
                        }}
                      >
                        {Math.floor(
                          trailer.duration_seconds / 60,
                        )}
                        m
                      </span>
                    </div>

                    {trailer.languages?.length > 1 && (
                      <div
                        style={{
                          marginTop: '8px',
                          display: 'flex',
                          gap: '8px',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '0.85rem',
                            color: 'var(--text-muted)',
                          }}
                        >
                          Audio:
                        </span>

                        {trailer.languages.map(
                          (lang: string) => (
                            <span
                              key={lang}
                              style={{
                                fontSize: '0.8rem',
                                padding: '2px 8px',
                                backgroundColor: '#2f2f2f',
                                borderRadius: '4px',
                              }}
                            >
                              {lang}
                            </span>
                          ),
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <h2>Seasons</h2>

        {show.seasons?.length === 0 && (
          <p
            className="text-muted"
            style={{ marginTop: '16px' }}
          >
            No seasons available.
          </p>
        )}

        {show.seasons?.map((season: any) => (
          <div
            key={season.season_number}
            style={{ marginTop: '24px' }}
          >
            <h3
              style={{
                marginBottom: '16px',
                color: 'var(--text-muted)',
              }}
            >
              Season {season.season_number}
            </h3>

            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
              }}
            >
              {season.episodes.map(
                (ep: any, i: number) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      gap: '24px',
                      padding: '16px',
                      backgroundColor: 'var(--bg-card)',
                      borderRadius: '8px',
                      alignItems: 'center',
                    }}
                  >
                    <div
                      style={{
                        flex: '0 0 160px',
                        position: 'relative',
                      }}
                    >
                      {ep.artwork?.thumbnail ? (
                        <img
                          src={getAssetUrl(
                            ep.artwork.thumbnail,
                          )}
                          alt={ep.title}
                          style={{
                            width: '100%',
                            borderRadius: '4px',
                          }}
                        />
                      ) : (
                        <div
                          className="image-skeleton"
                          style={{
                            width: '100%',
                            aspectRatio: '16/9',
                          }}
                        ></div>
                      )}

                      <div
                        style={{
                          position: 'absolute',
                          top: '50%',
                          left: '50%',
                          transform:
                            'translate(-50%, -50%)',
                        }}
                      >
                        <div
                          style={{
                            backgroundColor:
                              'rgba(0,0,0,0.5)',
                            borderRadius: '50%',
                            padding: '8px',
                          }}
                        >
                          <Play fill="white" size={24} />
                        </div>
                      </div>
                    </div>

                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent:
                            'space-between',
                        }}
                      >
                        <h4
                          style={{
                            fontSize: '1.1rem',
                            marginBottom: '8px',
                          }}
                        >
                          {ep.episode_number}. {ep.title}
                        </h4>

                        <span
                          style={{
                            color: 'var(--text-muted)',
                          }}
                        >
                          {Math.floor(
                            ep.duration_seconds / 60,
                          )}
                          m
                        </span>
                      </div>

                      {ep.languages?.length > 1 && (
                        <div
                          style={{
                            marginTop: '8px',
                            display: 'flex',
                            gap: '8px',
                          }}
                        >
                          <span
                            style={{
                              fontSize: '0.85rem',
                              color: 'var(--text-muted)',
                            }}
                          >
                            Audio:
                          </span>

                          {ep.languages.map(
                            (lang: string) => (
                              <span
                                key={lang}
                                style={{
                                  fontSize: '0.8rem',
                                  padding: '2px 8px',
                                  backgroundColor:
                                    '#2f2f2f',
                                  borderRadius: '4px',
                                }}
                              >
                                {lang}
                              </span>
                            ),
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ),
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};