import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  TextField,
  MenuItem,
  Box,
  Pagination,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  Button,
  Chip,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { ItemStatus, ItemCategory, Item } from '../types/item';
import api from '../utils/api';

// Utility function to truncate text
const truncateText = (text: string, maxLength: number = 120): string => {
  if (text.length <= maxLength) return text;
  
  // Find the last complete word before maxLength
  const truncated = text.substring(0, maxLength);
  const lastSpaceIndex = truncated.lastIndexOf(' ');
  
  if (lastSpaceIndex > 0) {
    return truncated.substring(0, lastSpaceIndex) + '...';
  }
  
  return truncated + '...';
};

// Mock data for demonstration
const mockItems: Item[] = [
  {
    id: '1',
    title: 'Lost iPhone 13',
    description: 'Blue iPhone 13 with a clear case. Lost near the library on Tuesday.',
    category: ItemCategory.ELECTRONICS,
    status: ItemStatus.LOST,
    location_found: 'Main Library',
    date_found: '2024-03-20',
    image_url: 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-13-blue-select-2021?wid=940&hei=1112&fmt=png-alpha&.v=1645036275334',
    finder_id: '1',
    created_at: '2024-03-20T10:30:00Z',
    user_id: '1',
    user: {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      created_at: '2024-01-01T00:00:00Z'
    }
  },
  {
    id: '2',
    title: 'Found Car Keys',
    description: 'Honda keys with a red keychain found in parking lot B.',
    category: ItemCategory.ACCESSORIES,
    status: ItemStatus.FOUND,
    location_found: 'Parking Lot B',
    date_found: '2024-03-19',
    image_url: 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
    finder_id: '2',
    created_at: '2024-03-19T14:20:00Z',
    user_id: '2',
    user: {
      id: '2',
      name: 'Jane Smith',
      email: 'jane@example.com',
      created_at: '2024-01-02T00:00:00Z'
    }
  },
  {
    id: '3',
    title: 'Lost Backpack',
    description: 'Black JanSport backpack with laptop inside. Lost in Student Center.',
    category: ItemCategory.OTHER,
    status: ItemStatus.LOST,
    location_found: 'Student Center',
    date_found: '2024-03-18',
    image_url: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
    finder_id: '3',
    created_at: '2024-03-18T09:15:00Z',
    user_id: '3',
    user: {
      id: '3',
      name: 'Michael Johnson',
      email: 'michael@example.com',
      created_at: '2024-01-03T00:00:00Z'
    }
  },
  {
    id: '4',
    title: 'Found Textbook',
    description: 'Calculus textbook found in classroom 205. Has "Sarah" written inside.',
    category: ItemCategory.BOOKS,
    status: ItemStatus.FOUND,
    location_found: 'Classroom 205',
    date_found: '2024-03-17',
    image_url: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
    finder_id: '4',
    created_at: '2024-03-17T16:45:00Z',
    user_id: '4',
    user: {
      id: '4',
      name: 'Emily Wilson',
      email: 'emily@example.com',
      created_at: '2024-01-04T00:00:00Z'
    }
  },
  {
    id: '5',
    title: 'Lost Wallet',
    description: 'Brown leather wallet with student ID inside. Lost in cafeteria.',
    category: ItemCategory.ACCESSORIES,
    status: ItemStatus.LOST,
    location_found: 'Main Cafeteria',
    date_found: '2024-03-16',
    image_url: 'https://images.unsplash.com/photo-1627123424574-724758594e93?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
    finder_id: '5',
    created_at: '2024-03-16T12:30:00Z',
    user_id: '5',
    user: {
      id: '5',
      name: 'David Brown',
      email: 'david@example.com',
      created_at: '2024-01-05T00:00:00Z'
    }
  },
  {
    id: '6',
    title: 'Found Earbuds',
    description: 'Apple AirPods found in the gym locker room.',
    category: ItemCategory.ELECTRONICS,
    status: ItemStatus.FOUND,
    location_found: 'Gym Locker Room',
    date_found: '2024-03-15',
    image_url: 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MME73?wid=1144&hei=1144&fmt=jpeg&qlt=90&.v=1632861342000',
    finder_id: '6',
    created_at: '2024-03-15T08:10:00Z',
    user_id: '6',
    user: {
      id: '6',
      name: 'Sarah Lopez',
      email: 'sarah@example.com',
      created_at: '2024-01-06T00:00:00Z'
    }
  },
];

const ItemList = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // Separate state for the input value and the actual search term used for API calls
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  
  const [category, setCategory] = useState<ItemCategory | ''>('');
  const [status, setStatus] = useState<ItemStatus | ''>('');

  // Function to get full image URL
  const getImageUrl = (imageUrl: string | null | undefined): string => {
    if (!imageUrl) return '';
    if (imageUrl.startsWith('http')) return imageUrl;
    return `http://localhost:8000${imageUrl}`;
  };

  // Debounce effect for search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput);
    }, 500); // Wait 500ms after user stops typing

    return () => clearTimeout(timer);
  }, [searchInput]);

  const fetchItems = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to fetch from API first
      try {
        const response = await api.get('/api/items', {
          params: {
            page,
            search: debouncedSearch,
            category,
            status,
          },
          timeout: 15000, // 15 second timeout for item fetching
        });
        
        // Backend already filters out returned items, so use response directly
        setItems(response.data.items || []);
        
        // Use total and per_page from backend response for correct pagination
        const totalItems = response.data.total || 0;
        const perPage = response.data.per_page || 10;
        setTotalPages(Math.ceil(totalItems / perPage));
      } catch (apiErr) {
        throw new Error('API request failed');
      }
    } catch (err) {
      console.log('API call failed, using mock data:', err);
      
      // Filter mock data based on search and filters
      let filteredItems = mockItems;
      
      if (debouncedSearch) {
        filteredItems = filteredItems.filter(item =>
          item.title.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
          item.description.toLowerCase().includes(debouncedSearch.toLowerCase())
        );
      }
      
      if (category) {
        filteredItems = filteredItems.filter(item => item.category === category);
      }
      
      if (status) {
        filteredItems = filteredItems.filter(item => item.status === status);
      }
      
      setItems(filteredItems);
      setTotalPages(1);
      setError('Using demo data - Backend not connected');
    } finally {
      setLoading(false);
    }
  };

  // Only trigger fetchItems when debouncedSearch changes, not searchInput
  useEffect(() => {
    fetchItems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, debouncedSearch, category, status, token]);

  const handleItemClick = (id: string) => {
    navigate(`/items/${id}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ my: { xs: 2, sm: 4 } }}>
        {/* Header Section - Mobile Optimized */}
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'row',
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: { xs: 3, sm: 4 },
          px: { xs: 2, sm: 0 }
        }}>
          <Typography 
            variant="h4" 
            gutterBottom={false}
            sx={{
              fontSize: { xs: '1.75rem', sm: '2.125rem' },
              fontWeight: 600,
              color: 'primary.main'
            }}
          >
            Lost & Found Items
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/create')}
            sx={{ 
              bgcolor: 'success.main',
              height: { xs: '44px', sm: '40px' },
              minWidth: { xs: '44px', sm: 'auto' },
              width: { xs: '44px', sm: 'auto' },
              fontSize: { xs: '0', sm: '0.875rem' },
              fontWeight: 500,
              borderRadius: { xs: '25%', sm: 1 },
              px: { xs: 0, sm: 2 },
              boxShadow: 2,
              '&:hover': {
                boxShadow: 3,
                bgcolor: 'success.dark'
              },
              '& .MuiButton-startIcon': {
                margin: { xs: 0, sm: '0 8px 0 -4px' }
              }
            }}
          >
            <Box sx={{ display: { xs: 'none', sm: 'inline' } }}>
              Report Item
            </Box>
          </Button>
        </Box>

        {/* Filters Section - Mobile Optimized */}
        <Box sx={{ 
          mb: { xs: 3, sm: 4 },
          px: { xs: 2, sm: 0 }
        }}>
          <Grid container spacing={{ xs: 2, sm: 2 }}>
            <Grid item xs={12} sm={12} md={4}>
              <TextField
                fullWidth
                label="Search items"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search by title or description..."
                helperText={searchInput !== debouncedSearch ? "Searching..." : ""}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: { xs: 2, sm: 1 },
                    height: { xs: '56px', sm: '48px' }
                  },
                  '& .MuiInputLabel-root': {
                    fontSize: { xs: '1rem', sm: '0.875rem' }
                  }
                }}
              />
            </Grid>
            <Grid item xs={6} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel 
                  id="category-select-label"
                  sx={{ fontSize: { xs: '1rem', sm: '0.875rem' } }}
                >
                  Category
                </InputLabel>
                <Select
                  labelId="category-select-label"
                  id="category-select"
                  value={category}
                  label="Category"
                  onChange={(e) => setCategory(e.target.value as ItemCategory)}
                  data-testid="category-select"
                  sx={{
                    borderRadius: { xs: 2, sm: 1 },
                    height: { xs: '56px', sm: '48px' }
                  }}
                >
                  <MenuItem value="" data-testid="category-option-all">All</MenuItem>
                  {Object.entries(ItemCategory).map(([key, value]) => (
                    <MenuItem key={key} value={value} data-testid={`category-option-${value}`}>
                      {value}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel sx={{ fontSize: { xs: '1rem', sm: '0.875rem' } }}>
                  Status
                </InputLabel>
                <Select
                  value={status}
                  label="Status"
                  onChange={(e) => setStatus(e.target.value as ItemStatus)}
                  sx={{
                    borderRadius: { xs: 2, sm: 1 },
                    height: { xs: '56px', sm: '48px' }
                  }}
                >
                  <MenuItem value="">All</MenuItem>
                  {Object.values(ItemStatus).map((stat) => (
                    <MenuItem key={stat} value={stat}>
                      {stat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>

        {error && (
          <Alert 
            severity="info" 
            sx={{ 
              mb: 2,
              mx: { xs: 2, sm: 0 },
              borderRadius: { xs: 2, sm: 1 }
            }}
          >
            {error}
          </Alert>
        )}

        {/* Items Grid - Mobile Optimized */}
        <Box sx={{ px: { xs: 1, sm: 0 } }}>
          <Grid container spacing={{ xs: 2, sm: 2, md: 3 }}>
            {items.length === 0 ? (
              <Grid item xs={12}>
                <Box sx={{ 
                  textAlign: 'center', 
                  py: { xs: 6, sm: 8 },
                  px: 2
                }}>
                  <Typography 
                    variant="h6" 
                    color="text.secondary"
                    sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }}
                  >
                    No items found
                  </Typography>
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ 
                      mt: 1,
                      fontSize: { xs: '0.875rem', sm: '1rem' }
                    }}
                  >
                    Try adjusting your search or filters
                  </Typography>
                </Box>
              </Grid>
            ) : (
              items.map((item) => (
                <Grid item key={item.id} xs={12} sm={6} md={4}>
                  <Card
                    sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      flexDirection: 'column',
                      cursor: 'pointer',
                      '&:hover': {
                        transform: 'scale(1.02)',
                        transition: 'transform 0.2s ease-in-out'
                      }
                    }}
                    onClick={() => handleItemClick(item.id)}
                  >
                    <CardMedia
                      component="img"
                      height="200"
                      image={getImageUrl(item.image_url)}
                      alt={item.title}
                      sx={{ objectFit: 'cover' }}
                    />
                    <CardContent sx={{ flexGrow: 1, pb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography gutterBottom variant="h6" component="h2" sx={{ mb: 0 }}>
                          {item.title}
                        </Typography>
                        <Chip 
                          label={item.status} 
                          color={item.status === 'lost' ? 'error' : 'success'}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {truncateText(item.description, 100)}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 'auto' }}>
                        <Chip 
                          label={item.category} 
                          variant="outlined" 
                          size="small" 
                          sx={{ mr: 1 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(item.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))
            )}
          </Grid>
        </Box>

        {/* Pagination - Mobile Optimized */}
        {totalPages > 1 && (
          <Box sx={{ 
            mt: { xs: 4, sm: 4 }, 
            display: 'flex', 
            justifyContent: 'center',
            px: { xs: 2, sm: 0 }
          }}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, value) => setPage(value)}
              color="primary"
              size="medium"
              sx={{
                '& .MuiPaginationItem-root': {
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  minWidth: { xs: '36px', sm: '40px' },
                  height: { xs: '36px', sm: '40px' }
                }
              }}
            />
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default ItemList;