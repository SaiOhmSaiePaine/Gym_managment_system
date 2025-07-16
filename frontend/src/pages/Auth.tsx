import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, 
  Button, 
  TextField, 
  Paper, 
  Tabs, 
  Tab, 
  CircularProgress, 
  Alert,
  IconButton,
  InputAdornment
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`auth-tabpanel-${index}`}
      aria-labelledby={`auth-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `auth-tab-${index}`,
    'aria-controls': `auth-tabpanel-${index}`,
  };
}

export default function Auth() {
  const navigate = useNavigate();
  const location = useLocation();
  const [tabValue, setTabValue] = useState(0);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordsMatch, setPasswordsMatch] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const { login, register, isLoading, error, isAuthenticated } = useAuth();
  
  // Redirect to home page or previous page if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location.state]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setFormError(null);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    
    try {
      await login(loginEmail, loginPassword);
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    
    if (registerPassword !== confirmPassword) {
      setPasswordsMatch(false);
      setFormError("Passwords don't match");
      return;
    }
    
    setPasswordsMatch(true);
    
    try {
      await register(registerName, registerEmail, registerPassword);
    } catch (err: any) {
      setFormError(err.message);
    }
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        maxWidth: 400, 
        margin: '0 auto', 
        mt: 4, 
        borderRadius: 2,
        overflow: 'hidden'
      }}
    >
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          variant="fullWidth"
          aria-label="authentication tabs"
        >
          <Tab label="Login" {...a11yProps(0)} />
          <Tab label="Register" {...a11yProps(1)} />
        </Tabs>
      </Box>
      
      {(formError || error) && (
        <Alert severity="error" sx={{ m: 2 }}>
          {formError || error}
        </Alert>
      )}
      
      <TabPanel value={tabValue} index={0}>
        <Box component="form" onSubmit={handleLogin} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="login-email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={loginEmail}
            onChange={(e) => setLoginEmail(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type={showLoginPassword ? 'text' : 'password'}
            id="login-password"
            autoComplete="current-password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setShowLoginPassword(!showLoginPassword)}
                    edge="end"
                    sx={{
                      '&:focus': {
                        outline: 'none'
                      },
                      '&:hover': {
                        backgroundColor: 'transparent'
                      }
                    }}
                  >
                    {!showLoginPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
          </Button>
        </Box>
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        <Box component="form" onSubmit={handleRegister} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="register-name"
            label="Full Name"
            name="name"
            autoComplete="name"
            autoFocus
            value={registerName}
            onChange={(e) => setRegisterName(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="register-email"
            label="Email Address"
            name="email"
            autoComplete="email"
            value={registerEmail}
            onChange={(e) => setRegisterEmail(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type={showRegisterPassword ? 'text' : 'password'}
            id="register-password"
            value={registerPassword}
            onChange={(e) => setRegisterPassword(e.target.value)}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setShowRegisterPassword(!showRegisterPassword)}
                    edge="end"
                    sx={{
                      '&:focus': {
                        outline: 'none'
                      },
                      '&:hover': {
                        backgroundColor: 'transparent'
                      }
                    }}
                  >
                    {!showRegisterPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="Confirm Password"
            type={showConfirmPassword ? 'text' : 'password'}
            id="confirm-password"
            error={!passwordsMatch}
            helperText={!passwordsMatch ? "Passwords don't match" : ''}
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              setPasswordsMatch(e.target.value === registerPassword);
            }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    edge="end"
                    sx={{
                      '&:focus': {
                        outline: 'none'
                      },
                      '&:hover': {
                        backgroundColor: 'transparent'
                      }
                    }}
                  >
                    {!showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Sign Up'}
          </Button>
        </Box>
      </TabPanel>
    </Paper>
  );
}
