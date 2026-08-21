import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { Home } from './pages/Home';
import { SearchPage } from './pages/SearchPage';
import { ShowDetail } from './pages/ShowDetail';
import { BrowsePage } from './pages/BrowsePage';

const Navbar: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Reset search bar when navigating away
  useEffect(() => {
    if (!location.pathname.includes('/search')) {
      setSearchQuery('');
      setSearchOpen(false);
    }
  }, [location.pathname]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <Link to="/" className="navbar-logo">PEBLO</Link>
      <ul className="navbar-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/series">Series</Link></li>
      </ul>
      <div className="navbar-right">
        {searchOpen ? (
          <form onSubmit={handleSearch} className="search-box">
            <Search size={18} color="white" />
            <input 
              type="text" 
              placeholder="Titles, people, genres" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
              onBlur={() => !searchQuery && setSearchOpen(false)}
            />
          </form>
        ) : (
          <Search size={22} color="white" style={{cursor: 'pointer'}} onClick={() => setSearchOpen(true)} />
        )}
      </div>
    </nav>
  );
};

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/series" element={<BrowsePage sectionName="series" title="Series" />} />
        <Route path="/films" element={<Navigate to="/" replace />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/title/:id" element={<ShowDetail />} />
      </Routes>
    </>
  );
}

export default App;
