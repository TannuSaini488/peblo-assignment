import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { ShowsList } from './pages/ShowsList';
import { ShowForm } from './pages/ShowForm';
import { PublishPage } from './pages/PublishPage';

// Stub pages
const Dashboard = () => <div className="p-8"><h1>Dashboard</h1><p>Welcome to Peblo TV CMS.</p></div>;

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="shows" element={<ShowsList />} />
        <Route path="shows/new" element={<ShowForm />} />
        <Route path="shows/:showId" element={<ShowForm />} />
        <Route path="publish" element={<PublishPage />} />
      </Route>
    </Routes>
  );
}

export default App;
