import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import '../list.css';

const SECTIONS = ['featured', 'series', 'minisodes', 'songs'];
const STATUSES = ['draft', 'published'];
const LANGUAGES = ['en', 'hi'];
const PAGE_SIZE = 10;

const isForbidden = (error: unknown) => {
  return typeof error === 'object' && error !== null && (error as any).response?.status === 403;
};

export const ShowsList: React.FC = () => {
  const [query, setQuery] = useState('');
  const [section, setSection] = useState('');
  const [status, setStatus] = useState('');
  const [language, setLanguage] = useState('');
  const [page, setPage] = useState(0);

  const params = {
    q: query || undefined,
    section: section || undefined,
    status: status || undefined,
    language: language || undefined,
    offset: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  };

  const { data: shows = [], isLoading, error } = useQuery({
    queryKey: ['shows', params],
    queryFn: async () => {
      const res = await apiClient.get('/admin/shows', { params });
      return res.data;
    }
  });

  const resetPage = (fn: () => void) => {
    setPage(0);
    fn();
  };

  if (isLoading) return <div className="p-8 text-muted">Loading shows...</div>;
  if (isForbidden(error)) return <div className="p-8 text-error">Permission denied. Your account cannot view CMS content.</div>;
  if (error) return <div className="p-8 text-error">Failed to load shows.</div>;

  return (
    <div className="p-8">
      <div className="flex-between mb-8">
        <h1>Shows</h1>
        <Link to="/shows/new" className="btn-primary flex-center gap-2">
          <Plus size={18} /> New Show
        </Link>
      </div>

      <div className="list-toolbar mb-8">
        <div className="list-search">
          <Search size={18} />
          <input
            value={query}
            onChange={(event) => resetPage(() => setQuery(event.target.value))}
            placeholder="Search title, slug, synopsis, category"
          />
        </div>
        <select value={section} onChange={(event) => resetPage(() => setSection(event.target.value))}>
          <option value="">All sections</option>
          {SECTIONS.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
        <select value={status} onChange={(event) => resetPage(() => setStatus(event.target.value))}>
          <option value="">All statuses</option>
          {STATUSES.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
        <select value={language} onChange={(event) => resetPage(() => setLanguage(event.target.value))}>
          <option value="">All languages</option>
          {LANGUAGES.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Slug</th>
              <th>Section</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {shows.map((show: any) => (
              <tr key={show.id}>
                <td>{show.title}</td>
                <td className="text-muted">{show.slug}</td>
                <td>{show.section || '-'}</td>
                <td>
                  <span className={`status-badge ${show.status}`}>{show.status}</span>
                </td>
                <td>
                  <Link to={`/shows/${show.id}`} className="btn-link">Edit</Link>
                </td>
              </tr>
            ))}
            {shows.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center text-muted py-4">No shows match these filters.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="pagination-bar">
        <button className="btn-secondary" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
        <span className="text-muted">Page {page + 1}</span>
        <button className="btn-secondary" disabled={shows.length < PAGE_SIZE} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
};
