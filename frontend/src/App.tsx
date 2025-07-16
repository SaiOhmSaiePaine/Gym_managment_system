// filepath: /Users/Linn/Documents/GitHub/example-lost-found-proj/frontend/src/App.tsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Button, Box, Avatar } from '@mui/material';
import { Person as PersonIcon } from '@mui/icons-material';
import ItemList from './pages/ItemList';
import ItemDetail from './pages/ItemDetail';
import CreateItem from './pages/CreateItem';
import Auth from './pages/Auth';
import AuthProvider, { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Header component with authentication status
const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  
  return (
    <AppBar position="static" sx={{ 
      boxShadow: 2,
      '@media (max-width:600px)': {
        position: 'sticky',
        top: 0,
        zIndex: 1100,
      }
    }}>
      <Toolbar sx={{
        minHeight: { xs: '56px', sm: '64px' },
        px: { xs: 2, sm: 3 }
      }}>
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1,
            fontSize: { xs: '1.1rem', sm: '1.25rem' },
            fontWeight: 500
          }}
        >
          Lost & Found Campus
        </Typography>
        
        {isAuthenticated ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              backgroundColor: 'rgba(255,255,255,0.1)',
              padding: '4px 12px',
              borderRadius: 1,
            }}>
              <Avatar sx={{ 
                width: 32, 
                height: 32,
                backgroundColor: 'primary.dark',
                fontSize: '1rem'
              }}>
                {user?.name?.charAt(0).toUpperCase()}
              </Avatar>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  display: { xs: 'none', sm: 'block' },
                  fontWeight: 500,
                  color: 'white'
                }}
              >
                {user?.name}
              </Typography>
            </Box>
            <Button 
              color="inherit" 
              onClick={logout}
              variant="outlined"
              size="small"
              sx={{
                height: 40,
                borderColor: 'rgba(255,255,255,0.5)',
                padding: '4px 12px',
                '&:hover': {
                  borderColor: 'rgba(255,255,255,0.8)',
                  backgroundColor: 'rgba(255,255,255,0.1)'
                }
              }}
            >
              Logout
            </Button>
          </Box>
        ) : (
          <Button 
            color="inherit" 
            href="/auth"
            startIcon={<PersonIcon />}
            variant="outlined"
            size="small"
            sx={{
              height: 40,
              borderColor: 'rgba(255,255,255,0.5)',
              padding: '4px 12px',
              '&:hover': {
                borderColor: 'rgba(255,255,255,0.8)',
                backgroundColor: 'rgba(255,255,255,0.1)'
              }
            }}
          >
            Login
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

function AppContent() {
  return (
    <div className="App">
      <Header />
      
      <Container 
        maxWidth="lg" 
        sx={{ 
          mt: { xs: 1, sm: 2 },
          px: { xs: 1, sm: 2, md: 3 },
          minHeight: 'calc(100vh - 56px)', // Adjust for mobile header height
          '@media (min-width:600px)': {
            minHeight: 'calc(100vh - 64px)', // Adjust for desktop header height
          }
        }}
      >
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
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
