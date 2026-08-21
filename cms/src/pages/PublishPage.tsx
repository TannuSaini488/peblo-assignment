import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { AlertCircle, CheckCircle } from 'lucide-react';

export const PublishPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [publishError, setPublishError] = useState('');

  const { data: report, isLoading: isReportLoading, error: reportError } = useQuery({
    queryKey: ['validation-report'],
    queryFn: async () => {
      const res = await apiClient.get('/admin/validation-report');
      return res.data;
    }
  });

  const { data: runs, isLoading: isRunsLoading, error: runsError } = useQuery({
    queryKey: ['publish-runs'],
    queryFn: async () => {
      const res = await apiClient.get('/admin/catalog/publish-runs');
      return res.data;
    }
  });

  const publishMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/admin/catalog/publish');
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['publish-runs'] });
      setPublishError('');
    },
    onError: (error: any) => {
      if (error.response?.status === 403) {
        setPublishError('Permission denied. Only admins can publish.');
        return;
      }
      setPublishError(error.response?.data?.detail || 'Publish failed');
    }
  });

  if (isReportLoading || isRunsLoading) return <div className="p-8">Loading...</div>;
  if ((reportError as any)?.response?.status === 403 || (runsError as any)?.response?.status === 403) {
    return <div className="p-8 text-error">Permission denied. Your account cannot view publish controls.</div>;
  }
  if (reportError || runsError) return <div className="p-8 text-error">Failed to load publish status.</div>;

  const hasBlockingErrors = report?.blocking_errors?.length > 0;

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex-between mb-8">
        <h1>Publish Catalogue</h1>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
          <button 
            className="btn-primary" 
            disabled={hasBlockingErrors || publishMutation.isPending}
            onClick={() => publishMutation.mutate()}
          >
            {publishMutation.isPending ? 'Publishing...' : 'Publish Now'}
          </button>
          {hasBlockingErrors && <span className="text-error">Resolve blocking validation errors before publishing.</span>}
        </div>
      </div>

      {publishError && (
        <div className="alert alert-error mb-8">
          <AlertCircle size={20} />
          <span>{publishError}</span>
        </div>
      )}

      <div className="card mb-8">
        <h2 className="card-title">Validation Report</h2>
        
        {hasBlockingErrors ? (
          <div className="alert alert-error mb-4">
            <AlertCircle size={20} />
            <span>Publishing is blocked. Please resolve the following errors.</span>
          </div>
        ) : (
          <div className="alert alert-success mb-4">
            <CheckCircle size={20} />
            <span>Ready to publish. No blocking errors found.</span>
          </div>
        )}

        {hasBlockingErrors && (
          <div className="error-list">
            {report.blocking_errors.map((err: any, i: number) => (
              <div key={i} className="error-item">
                <div className="error-context">
                  <strong>{err.show_title}</strong> 
                  {err.season_number !== null && <span> - Season {err.season_number}</span>}
                  {err.episode_title && <span> - {err.episode_title}</span>}
                </div>
                <div className="error-message">{err.message}</div>
              </div>
            ))}
          </div>
        )}

        {report?.warnings?.length > 0 && (
          <div className="mt-8">
            <h3>Warnings (Non-blocking)</h3>
            <ul className="warning-list mt-4">
              {report.warnings.map((warn: any, i: number) => (
                <li key={i} className="warning-item">{warn.message}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">Publish History</h2>
        <div className="table-container mt-4">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Outcome</th>
                <th>Shows</th>
                <th>Episodes</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {runs?.map((run: any) => (
                <tr key={run.id}>
                  <td>{new Date(run.published_at).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge ${run.outcome === 'success' ? 'published' : 'draft'}`}>
                      {run.outcome}
                    </span>
                  </td>
                  <td>{run.show_count}</td>
                  <td>{run.episode_count}</td>
                  <td className="text-error">{run.error_message || '-'}</td>
                </tr>
              ))}
              {runs?.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center text-muted py-4">No history found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
