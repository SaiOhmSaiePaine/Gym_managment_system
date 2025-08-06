import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Card,
  CardMedia,
  Typography,
  Button,
  Box,
  CircularProgress,
  Alert,
  Grid,
  Chip,
  Paper,
  Avatar
} from '@mui/material';
import { ArrowBack, LocationOn, DateRange, Category, Flag, Person } from '@mui/icons-material';
import { Item, ItemCustodyStatus } from '../types/item';
import { API_BASE_URL } from '../config';
import { getImageUrl } from '../util/image';
import { useAuth } from '../context/AuthContext';

const ItemDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/items/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch item details');
        }
        const data = await response.json();
        setItem(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchItem();
  }, [id]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Helper function to get location from either field
  const getLocation = (item: Item): string => {
    return item.location_found || item.location || 'Location not specified';
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Box sx={{ mt: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button onClick={() => navigate('/')} startIcon={<ArrowBack />}>
            Back to Items
          </Button>
        </Box>
      </Container>
    );
  }

  if (!item) {
    return (
      <Container>
        <Box sx={{ mt: 4 }}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Item not found
          </Alert>
          <Button onClick={() => navigate('/')} startIcon={<ArrowBack />}>
            Back to Items
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ my: 4 }}>
        <Button 
          onClick={() => navigate('/')} 
          startIcon={<ArrowBack />}
          sx={{ mb: 3 }}
        >
          Back to Items
        </Button>

        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardMedia
                component="img"
                image={getImageUrl(item.image_url)}
                alt={item.title}
                sx={{ 
                  backgroundColor: '#f5f5f5',
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain'
                }}
              />
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h4" gutterBottom>
                {item.title}
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Chip
                  label={item.status}
                  color={item.status === 'lost' ? 'error' : 'success'}
                  sx={{ mr: 1, mb: 1 }}
                />
                <Chip
                  label={item.category}
                  variant="outlined"
                  sx={{ mb: 1 }}
                />
              </Box>
              
              {/* User who posted the item */}
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 3,
                p: 2,
                bgcolor: 'background.default',
                borderRadius: 1
              }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Person />
                </Avatar>
                <Typography variant="body1" fontWeight="medium">
                  {item.user_name || (item.user && item.user.name) || 'Unknown User'}
                </Typography>
              </Box>

              <Typography variant="h6" gutterBottom>
                Description
              </Typography>
              <Typography variant="body1" paragraph sx={{ flexGrow: 1 }}>
                {item.description}
              </Typography>

              <Box sx={{ mt: 'auto' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    <strong>Location:</strong> {getLocation(item)}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <DateRange sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    <strong>Date:</strong> {formatDate(item.date_found)}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Category sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    <strong>Category:</strong> {item.category}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Flag sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    <strong>Status:</strong> {item.status}
                  </Typography>
                </Box>

                {/* Show custody status for found items */}
                {item.status === 'found' && item.custody_status && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Typography variant="body1" sx={{ bgcolor: 'info.light', color: 'info.contrastText', px: 2, py: 1, borderRadius: 1 }}>
                      <strong>Item Location:</strong> {
                        item.custody_status === ItemCustodyStatus.KEPT_BY_FINDER ? 'With Finder' :
                        item.custody_status === ItemCustodyStatus.HANDED_TO_ONE_STOP ? 'At One-Stop Center' :
                        'Left at Original Location'
                      }
                    </Typography>
                  </Box>
                )}

                {/* Only show contact button if current user is not the item reporter */}
                {currentUser && currentUser.id !== item.user_id ? (
                  // For found items, show different contact options based on custody status
                  item.status === 'found' && item.custody_status ? (
                    item.custody_status === ItemCustodyStatus.KEPT_BY_FINDER ? (
                      <Button 
                        variant="contained" 
                        color="primary" 
                        fullWidth
                        onClick={() => {
                          // Future: Add contact functionality
                          alert('Contact finder - they have the item with them!');
                        }}
                      >
                        Contact Finder
                      </Button>
                    ) : (
                      <Button 
                        variant="contained" 
                        color="secondary" 
                        fullWidth
                        onClick={() => {
                          // Future: Add admin contact functionality
                          const location = item.custody_status === ItemCustodyStatus.HANDED_TO_ONE_STOP 
                            ? 'One-Stop Center' 
                            : 'original location';
                          alert(`Contact Admin - Item is at ${location}`);
                        }}
                      >
                        Contact Admin
                      </Button>
                    )
                  ) : (
                    // For lost items or found items without custody status
                    <Button 
                      variant="contained" 
                      color="primary" 
                      fullWidth
                      onClick={() => {
                        // Future: Add contact functionality
                        alert('Contact functionality coming soon!');
                      }}
                    >
                      Contact {item.status === 'lost' ? 'Owner' : 'Finder'}
                    </Button>
                  )
                ) : currentUser && currentUser.id === item.user_id ? (
                  <Box sx={{ 
                    p: 2, 
                    bgcolor: 'background.default', 
                    borderRadius: 1, 
                    textAlign: 'center',
                    border: '1px solid',
                    borderColor: 'divider'
                  }}>
                    <Typography variant="body2" color="text.secondary">
                      This is your {item.status === 'lost' ? 'lost' : 'found'} item
                    </Typography>
                  </Box>
                ) : (
                  <Button 
                    variant="outlined" 
                    fullWidth
                    disabled
                  >
                    Login to Contact {item.status === 'lost' ? 'Owner' : 'Finder'}
                  </Button>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ItemDetail;