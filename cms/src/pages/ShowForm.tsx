import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Trash2, Upload, X, ChevronDown, ChevronUp, Plus } from 'lucide-react';

const SECTIONS = ['featured', 'series', 'minisodes', 'songs'];
const CATEGORIES = [
  'adventure', 'folk', 'friendship', 'india', 'language',
  'learning', 'maths', 'music', 'nature', 'reading',
  'science', 'singalong', 'stories', 'travel', 'values'
];
const LANGUAGES = ['en', 'hi'];
const STATUSES = ['draft', 'published'];

const ARTWORK_SPECS: Record<string, { aspect: string; target: string; label: string }> = {
  poster:    { aspect: '2:3',  target: '~600×900',   label: 'Poster' },
  banner:    { aspect: '16:9', target: '~1280×720',  label: 'Banner' },
  thumbnail: { aspect: '16:9', target: '~640×360',   label: 'Thumbnail' },
};

interface ArtworkRecord {
  id: string;
  artwork_type: string;
  storage_key: string;
  original_filename: string;
  width: number;
  height: number;
  file_size_bytes: number;
}

interface EpisodeRecord {
  id: string;
  episode_number: number;
  episode_title: string;
  duration_seconds: number | null;
  language: string;
  content_group: string;
  status: string;
  artwork: ArtworkRecord[];
}

interface SeasonRecord {
  id: string;
  season_number: number;
}

/* ─── Show Form ──────────────────────────────── */
export const ShowForm: React.FC = () => {
  const { showId } = useParams();
  const isNew = !showId || showId === 'new';
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [section, setSection] = useState('');
  const [categories, setCategories] = useState<string[]>([]);
  const [synopsis, setSynopsis] = useState('');
  const [status, setStatus] = useState('draft');
  const [error, setError] = useState('');

  // Seasons / episodes expansion
  const [expandedSeason, setExpandedSeason] = useState<string | null>(null);

  // Fetch show data for editing
  const { data: show, isLoading, error: showLoadError } = useQuery({
    queryKey: ['show', showId],
    queryFn: async () => {
      const res = await apiClient.get(`/admin/shows/${showId}`);
      return res.data;
    },
    enabled: !isNew,
  });

  // Fetch seasons for this show
  const { data: seasons } = useQuery({
    queryKey: ['seasons', showId],
    queryFn: async () => {
      const res = await apiClient.get(`/admin/shows/${showId}/seasons`);
      return res.data as SeasonRecord[];
    },
    enabled: !isNew,
  });

  useEffect(() => {
    if (show) {
      setTitle(show.title);
      setSlug(show.slug);
      setSection(show.section || '');
      setCategories(show.categories || []);
      setSynopsis(show.synopsis || '');
      setStatus(show.status || 'draft');
    }
  }, [show]);

  const autoSlug = useCallback((t: string) => {
    return t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }, []);

  // Save / update
  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = { title, slug, section: section || null, categories, synopsis, status };
      if (isNew) {
        return (await apiClient.post('/admin/shows', payload)).data;
      } else {
        return (await apiClient.put(`/admin/shows/${showId}`, payload)).data;
      }
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['shows'] });
      if (isNew) navigate(`/shows/${data.id}`, { replace: true });
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to save show');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete(`/admin/shows/${showId}`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['shows'] });
      navigate('/shows');
    },
  });

  if (!isNew && isLoading) return <div className="p-8 text-muted">Loading show...</div>;
  if (!isNew && (showLoadError as any)?.response?.status === 403) {
    return <div className="p-8 text-error">Permission denied. Your account cannot edit this show.</div>;
  }
  if (!isNew && showLoadError) return <div className="p-8 text-error">Failed to load show.</div>;

  return (
    <div className="p-8" style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Header */}
      <div className="flex-between mb-8">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button onClick={() => navigate('/shows')} className="btn-icon" title="Back">
            <ArrowLeft size={20} />
          </button>
          <h1>{isNew ? 'New Show' : `Edit: ${show?.title || ''}`}</h1>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {!isNew && (
            <button onClick={() => { if (window.confirm('Delete this show?')) deleteMutation.mutate(); }} className="btn-danger">
              <Trash2 size={16} /> Delete
            </button>
          )}
          <button onClick={() => saveMutation.mutate()} className="btn-primary" disabled={saveMutation.isPending}>
            <Save size={16} /> {saveMutation.isPending ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>

      {error && <div className="form-error mb-4">{error}</div>}

      {/* Form Fields */}
      <div className="form-card">
        <div className="form-group">
          <label className="form-label">Title *</label>
          <input
            className="form-input"
            value={title}
            onChange={e => { setTitle(e.target.value); if (isNew) setSlug(autoSlug(e.target.value)); }}
            placeholder="Show title"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Slug *</label>
          <input className="form-input" value={slug} onChange={e => setSlug(e.target.value)} placeholder="show-slug" />
        </div>

        <div className="form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Section</label>
            <select className="form-input" value={section} onChange={e => setSection(e.target.value)}>
              <option value="">— No section —</option>
              {SECTIONS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Status</label>
            <select className="form-input" value={status} onChange={e => setStatus(e.target.value)}>
              {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Categories</label>
          <div className="checkbox-grid">
            {CATEGORIES.map(cat => (
              <label key={cat} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={categories.includes(cat)}
                  onChange={e => {
                    if (e.target.checked) setCategories([...categories, cat]);
                    else setCategories(categories.filter(c => c !== cat));
                  }}
                />
                {cat}
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Synopsis</label>
          <textarea
            className="form-input form-textarea"
            value={synopsis}
            onChange={e => setSynopsis(e.target.value)}
            rows={4}
            placeholder="Brief description of the show…"
          />
        </div>
      </div>

      {/* Seasons & Episodes (only when editing existing show) */}
      {!isNew && (
        <div style={{ marginTop: 32 }}>
          <div className="flex-between mb-4">
            <h2>Seasons &amp; Episodes</h2>
            <AddSeasonButton showId={showId!} />
          </div>
          {seasons?.length === 0 && <p className="text-muted">No seasons yet.</p>}
          {seasons?.map((season: SeasonRecord) => (
            <SeasonCard
              key={season.id}
              season={season}
              showId={showId!}
              isExpanded={expandedSeason === season.id}
              onToggle={() => setExpandedSeason(expandedSeason === season.id ? null : season.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/* ─── Add Season Button ──────────────────────── */
const AddSeasonButton: React.FC<{ showId: string }> = ({ showId }) => {
  const [num, setNum] = useState('');
  const [open, setOpen] = useState(false);
  const qc = useQueryClient();
  const mutation = useMutation({
    mutationFn: async () => {
      await apiClient.post(`/admin/shows/${showId}/seasons`, { season_number: parseInt(num) });
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['seasons', showId] }); setOpen(false); setNum(''); },
  });
  if (!open) return <button className="btn-secondary" onClick={() => setOpen(true)}><Plus size={16} /> Add Season</button>;
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <input className="form-input" style={{ width: 80 }} type="number" value={num} onChange={e => setNum(e.target.value)} placeholder="#" />
      <button className="btn-primary" onClick={() => mutation.mutate()} disabled={!num}>Add</button>
      <button className="btn-icon" onClick={() => setOpen(false)}><X size={16} /></button>
    </div>
  );
};

/* ─── Season Card ────────────────────────────── */
const SeasonCard: React.FC<{
  season: SeasonRecord;
  showId: string;
  isExpanded: boolean;
  onToggle: () => void;
}> = ({ season, showId, isExpanded, onToggle }) => {
  const qc = useQueryClient();

  const { data: episodes } = useQuery({
    queryKey: ['episodes', season.id],
    queryFn: async () => {
      const res = await apiClient.get(`/admin/seasons/${season.id}/episodes`);
      return res.data as EpisodeRecord[];
    },
    enabled: isExpanded,
  });

  const deleteSeason = useMutation({
    mutationFn: async () => { await apiClient.delete(`/admin/seasons/${season.id}`); },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['seasons', showId] }),
  });

  return (
    <div className="form-card" style={{ marginBottom: 12 }}>
      <div className="flex-between" style={{ cursor: 'pointer' }} onClick={onToggle}>
        <h3>Season {season.season_number}{season.season_number === 0 ? ' (Trailers)' : ''}</h3>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button className="btn-icon btn-danger-icon" title="Delete season" onClick={e => { e.stopPropagation(); if (window.confirm('Delete this season?')) deleteSeason.mutate(); }}>
            <Trash2 size={14} />
          </button>
          {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </div>

      {isExpanded && (
        <div style={{ marginTop: 16 }}>
          <AddEpisodeButton seasonId={season.id} />
          {episodes?.length === 0 && <p className="text-muted" style={{ marginTop: 8 }}>No episodes in this season.</p>}
          {episodes?.map(ep => <EpisodeRow key={ep.id} episode={ep} seasonId={season.id} />)}
        </div>
      )}
    </div>
  );
};

/* ─── Add Episode ────────────────────────────── */
const AddEpisodeButton: React.FC<{ seasonId: string }> = ({ seasonId }) => {
  const [open, setOpen] = useState(false);
  const [epNum, setEpNum] = useState('');
  const [epTitle, setEpTitle] = useState('');
  const [lang, setLang] = useState('en');
  const [cg, setCg] = useState('');
  const [dur, setDur] = useState('');
  const qc = useQueryClient();
  const mutation = useMutation({
    mutationFn: async () => {
      await apiClient.post(`/admin/seasons/${seasonId}/episodes`, {
        episode_number: parseInt(epNum),
        episode_title: epTitle,
        language: lang,
        content_group: cg,
        duration_seconds: dur ? parseInt(dur) : null,
        status: 'published',
      });
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['episodes', seasonId] }); setOpen(false); },
  });
  if (!open) return <button className="btn-secondary btn-sm" onClick={() => setOpen(true)}><Plus size={14} /> Add Episode</button>;
  return (
    <div className="form-card" style={{ background: 'var(--bg-hover)', padding: 16, marginBottom: 12 }}>
      <div className="form-row">
        <input className="form-input" style={{ width: 70 }} type="number" placeholder="#" value={epNum} onChange={e => setEpNum(e.target.value)} />
        <input className="form-input" style={{ flex: 1 }} placeholder="Episode title" value={epTitle} onChange={e => setEpTitle(e.target.value)} />
        <select className="form-input" style={{ width: 80 }} value={lang} onChange={e => setLang(e.target.value)}>
          {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>
      <div className="form-row" style={{ marginTop: 8 }}>
        <input className="form-input" style={{ flex: 1 }} placeholder="Content group" value={cg} onChange={e => setCg(e.target.value)} />
        <input className="form-input" style={{ width: 100 }} type="number" placeholder="Duration (s)" value={dur} onChange={e => setDur(e.target.value)} />
        <button className="btn-primary btn-sm" onClick={() => mutation.mutate()}>Add</button>
        <button className="btn-icon" onClick={() => setOpen(false)}><X size={16} /></button>
      </div>
    </div>
  );
};

/* ─── Episode Row ────────────────────────────── */
const EpisodeRow: React.FC<{ episode: EpisodeRecord; seasonId: string }> = ({ episode, seasonId }) => {
  const [showArtwork, setShowArtwork] = useState(false);
  const qc = useQueryClient();

  const deleteMut = useMutation({
    mutationFn: async () => { await apiClient.delete(`/admin/episodes/${episode.id}`); },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['episodes', seasonId] }),
  });

  return (
    <div className="episode-row">
      <div className="flex-between">
        <div>
          <span className="text-muted" style={{ marginRight: 8 }}>E{episode.episode_number}</span>
          <strong>{episode.episode_title}</strong>
          <span className="text-muted" style={{ marginLeft: 8 }}>({episode.language})</span>
          {episode.duration_seconds && <span className="text-muted" style={{ marginLeft: 8 }}>{Math.floor(episode.duration_seconds / 60)}m{episode.duration_seconds % 60}s</span>}
          <span className={`status-badge ${episode.status}`} style={{ marginLeft: 8 }}>{episode.status}</span>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          <button className="btn-secondary btn-sm" onClick={() => setShowArtwork(!showArtwork)}>
            {showArtwork ? 'Hide' : 'Artwork'} ({episode.artwork?.length || 0}/3)
          </button>
          <button className="btn-icon btn-danger-icon" title="Delete episode" onClick={() => { if (window.confirm('Delete?')) deleteMut.mutate(); }}>
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {showArtwork && <ArtworkPanel episodeId={episode.id} artwork={episode.artwork || []} seasonId={seasonId} />}
    </div>
  );
};

/* ─── Artwork Panel ──────────────────────────── */
const ArtworkPanel: React.FC<{ episodeId: string; artwork: ArtworkRecord[]; seasonId: string }> = ({ episodeId, artwork, seasonId }) => {
  return (
    <div className="artwork-panel">
      {Object.entries(ARTWORK_SPECS).map(([type, spec]) => {
        const existing = artwork.find(a => a.artwork_type === type);
        return (
          <ArtworkSlot
            key={type}
            episodeId={episodeId}
            type={type}
            spec={spec}
            existing={existing || null}
            seasonId={seasonId}
          />
        );
      })}
    </div>
  );
};

/* ─── Artwork Slot ───────────────────────────── */
const ArtworkSlot: React.FC<{
  episodeId: string;
  type: string;
  spec: { aspect: string; target: string; label: string };
  existing: ArtworkRecord | null;
  seasonId: string;
}> = ({ episodeId, type, spec, existing, seasonId }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const qc = useQueryClient();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError('');
    const formData = new FormData();
    formData.append('file', file);
    try {
      await apiClient.post(`/admin/episodes/${episodeId}/artwork/${type}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      qc.invalidateQueries({ queryKey: ['episodes', seasonId] });
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!existing) return;
    await apiClient.delete(`/admin/artwork/${existing.id}`);
    qc.invalidateQueries({ queryKey: ['episodes', seasonId] });
  };

  const previewUrl = existing ? `${apiClient.defaults.baseURL}/storage/${existing.storage_key}` : null;

  return (
    <div className="artwork-slot">
      <div className="artwork-slot-header">
        <strong>{spec.label}</strong>
        <span className="text-muted">{spec.aspect} • {spec.target} • max 200 KB</span>
      </div>

      {previewUrl && (
        <div className="artwork-preview">
          <img src={previewUrl} alt={`${spec.label} preview`} />
        </div>
      )}

      {existing && (
        <div className="text-muted" style={{ fontSize: '0.75rem', marginBottom: 4 }}>
          {existing.original_filename} • {existing.width}×{existing.height} • {(existing.file_size_bytes / 1024).toFixed(1)} KB
        </div>
      )}

      {uploadError && <div className="form-error" style={{ fontSize: '0.8rem' }}>{uploadError}</div>}

      <div style={{ display: 'flex', gap: 8 }}>
        <label className="btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
          <Upload size={14} /> {uploading ? 'Uploading…' : existing ? 'Replace' : 'Upload'}
          <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleUpload} disabled={uploading} />
        </label>
        {existing && (
          <button className="btn-icon btn-danger-icon" title="Remove artwork" onClick={handleDelete}>
            <X size={14} />
          </button>
        )}
      </div>
    </div>
  );
};
