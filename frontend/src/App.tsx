// filepath: /Users/Linn/Documents/GitHub/example-lost-found-proj/frontend/src/App.tsx
import React, { useEffect } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Person as PersonIcon } from '@mui/icons-material';
import ItemList from './pages/ItemList';
import ItemDetail from './pages/ItemDetail';
import CreateItem from './pages/CreateItem';
import Auth from './pages/Auth';
import AdminRedirect from './pages/AdminRedirect';
import AdminTest from './pages/AdminTest';
import AuthProvider, { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Clean, simple header
const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        backgroundColor: 'white',
        borderBottom: '1px solid var(--gray-200)',
        color: 'var(--gray-900)'
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{
          minHeight: '64px',
          justifyContent: 'space-between'
        }}>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              fontWeight: 600,
              color: 'var(--gray-900)'
            }}
          >
            Lost & Found Campus
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isAuthenticated ? (
              <>
                <Typography variant="body2" color="text.secondary">
                  Welcome, {user?.name}
                </Typography>
                <Button 
                  color="inherit" 
                  onClick={logout}
                  variant="outlined"
                  size="small"
                >
                  Logout
                </Button>
              </>
            ) : (
              <Button 
                color="inherit" 
                onClick={() => navigate('/auth')}
                startIcon={<PersonIcon />}
                variant="outlined"
                size="small"
              >
                Login
              </Button>
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

function App() {
  console.log('App component rendering, checking routes');
  const location = useLocation();
  
  useEffect(() => {
    // Handle admin routes by redirecting to static HTML page
    if (location.pathname.startsWith('/admin')) {
      window.location.href = '/admin-redirect.html';
    }
  }, [location]);
  
  return (
    <AuthProvider>
      <div className="App">
        <Routes>
          {/* Admin routes */}
            <Route path="/admin-test" element={<AdminTest />} />
            
            {/* Regular App Routes - With Header */}
            <Route path="/*" element={
              <>
                <Header />
                <Box sx={{ minHeight: 'calc(100vh - 64px)' }}>
                  <Container maxWidth="xl" sx={{ py: 3 }}>
                    <Routes>
                      <Route path="/" element={<ItemList />} />
                      <Route path="/items" element={<ItemList />} />
                      <Route path="/items/:id" element={<ItemDetail />} />
                      <Route path="/create" element={
                        <ProtectedRoute>
                          <CreateItem />
                        </ProtectedRoute>
                      } />
                      <Route path="/auth" element={<Auth />} />
                    </Routes>
                  </Container>
                </Box>
              </>
            } />
          </Routes>
        </div>
      </AuthProvider>
  );
}

export default App;
