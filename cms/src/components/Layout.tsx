import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Film, Send, LogOut } from 'lucide-react';

export const Layout: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Peblo TV <span>CMS</span></h2>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} end>
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/shows" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            <Film size={20} />
            <span>Shows</span>
          </NavLink>
          <NavLink to="/publish" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            <Send size={20} />
            <span>Publish</span>
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <button className="btn-logout" onClick={handleLogout}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
      
      <main className="main-content">
        <header className="top-header">
          <div className="header-title">
            {/* Title can be dynamic based on route later */}
            <h1>Content Management</h1>
          </div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
