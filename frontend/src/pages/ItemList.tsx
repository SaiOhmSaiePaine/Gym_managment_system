import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
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
  Paper,
  IconButton,
  InputAdornment,
  ListItem,
  Chip,
  Grid,
  Card,
  CardContent,
  CardMedia,
} from '@mui/material';
import { 
  Add, 
  Search, 
  ViewList,
  ViewModule,
  ImageNotSupported
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { ItemStatus, ItemCategory, Item } from '../types/item';
import { getImageUrl } from '../util/image';
import api from '../util/api';

const ItemList = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('grid');
  
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  const [category, setCategory] = useState<ItemCategory | ''>('');
  const [status, setStatus] = useState<ItemStatus | ''>('');

  const truncateText = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  };

  const handleSearchKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      setSearchTerm(searchInput);
      setPage(1);
    }
  };

  const handleItemClick = (itemId: string) => {
    navigate(`/items/${itemId}`);
  };

  const fetchItems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '25',
        ...(searchTerm && { search: searchTerm }),
        ...(category && { category }),
        ...(status && { status }),
      });

      const response = await api.get(`/api/items?${params.toString()}`);
      setItems(response.data.items || []);
      setTotalPages(response.data.pages || 1);
    } catch (err: any) {
      console.error('Failed to fetch items:', err);
      setError(err.response?.data?.error || 'No items found matching your criteria');
    } finally {
      setLoading(false);
    }
  }, [page, searchTerm, category, status]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const renderGridView = () => {
    if (items.length === 0) {
      return (
        <Box sx={{ p: 6, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
            No items found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search or filters
          </Typography>
        </Box>
      );
    }

    return (
      <Grid container spacing={3}>
        {items.map((item) => (
          <Grid item xs={12} sm={6} md={4} key={item.id}>
            <Card
              className="clean-card"
              sx={{
                height: '100%',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                }
              }}
              onClick={() => handleItemClick(item.id)}
            >
              {/* Card Image */}
              {getImageUrl(item.image_url) === '/placeholder.png' ? (
                <Box
                  sx={{
                    height: 280,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'var(--gray-100)',
                    borderBottom: '1px solid var(--gray-200)'
                  }}
                >
                  <ImageNotSupported sx={{ color: 'var(--gray-400)', fontSize: 64 }} />
                </Box>
              ) : (
                <CardMedia
                  component="img"
                  height="280"
                  image={getImageUrl(item.image_url)}
                  alt={item.title}
                  sx={{ 
                    objectFit: 'cover',
                    transition: 'transform 0.2s ease',
                    '&:hover': {
                      transform: 'scale(1.02)'
                    }
                  }}
                />
              )}

              <CardContent sx={{ flexGrow: 1, p: 3 }}>
                {/* Status indicator bar */}
                <Box
                  sx={{
                    width: '100%',
                    height: '4px',
                    backgroundColor: item.status === ItemStatus.LOST ? 'var(--status-lost)' :
                      item.status === ItemStatus.FOUND ? 'var(--status-found)' :
                      'var(--status-returned)',
                    mb: 2,
                    borderRadius: '2px'
                  }}
                />

                {/* Simplified content - only item name and status */}
                <Typography variant="h6" sx={{ 
                  fontWeight: 600, 
                  color: 'var(--gray-900)', 
                  mb: 2, 
                  lineHeight: 1.3,
                  textAlign: 'center'
                }}>
                  {item.title}
                </Typography>

                {/* Status indicator - centered */}
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <div className={`status-indicator status-${item.status}`} style={{ fontSize: '0.9rem' }}>
                    {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                  </div>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  const renderListView = () => {
    if (items.length === 0) {
      return (
        <Box sx={{ p: 6, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
            No items found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search or filters
          </Typography>
        </Box>
      );
    }

    return (
      <>
        {items.map((item, index) => (
          <ListItem
            key={item.id}
            sx={{
              borderLeft: `4px solid ${
                item.status === ItemStatus.LOST ? 'var(--status-lost)' :
                item.status === ItemStatus.FOUND ? 'var(--status-found)' :
                'var(--status-returned)'
              }`,
              borderBottom: index < items.length - 1 ? '1px solid var(--gray-100)' : 'none',
              cursor: 'pointer',
              py: 3,
              '&:hover': {
                backgroundColor: 'var(--gray-50)'
              }
            }}
            onClick={() => handleItemClick(item.id)}
          >
            <Box sx={{ display: 'flex', gap: 4, width: '100%', alignItems: 'center' }}>
              {/* Item Image */}
              <Box sx={{ flexShrink: 0 }}>
                {getImageUrl(item.image_url) === '/placeholder.png' ? (
                  <Box
                    sx={{
                      width: 140,
                      height: 140,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: 'var(--gray-100)',
                      borderRadius: 'var(--radius-lg)',
                      border: '2px solid var(--gray-200)'
                    }}
                  >
                    <ImageNotSupported sx={{ color: 'var(--gray-400)', fontSize: 40 }} />
                  </Box>
                ) : (
                  <img
                    src={getImageUrl(item.image_url)}
                    alt={item.title}
                    style={{
                      width: '140px',
                      height: '140px',
                      objectFit: 'cover',
                      borderRadius: 'var(--radius-lg)',
                      border: '2px solid var(--gray-200)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                    }}
                  />
                )}
              </Box>

              {/* Item Details */}
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" sx={{ color: 'var(--gray-600)', fontSize: '0.75rem', mb: 0.5 }}>
                  {item.id.split('-')[0].toUpperCase()}-{item.category.toUpperCase()}
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'var(--gray-900)', mb: 1 }}>
                  {item.title}
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1, flexWrap: 'wrap' }}>
                  <Typography variant="body2" color="text.secondary">
                    {item.status === ItemStatus.LOST ? 'Lost by' : 'Found by'} {item.user_name || 'Unknown'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">•</Typography>
                  <Typography variant="body2" color="text.secondary">
                    📍 {item.location_found}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">•</Typography>
                  <Typography variant="body2" color="text.secondary">
                    📅 {new Date(item.date_found).toLocaleDateString()}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {truncateText(item.description, 120)}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <div className={`status-indicator status-${item.status}`}>
                    {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                  </div>
                  <Chip
                    label={item.category}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: '0.7rem' }}
                  />
                </Box>
              </Box>
            </Box>
          </ListItem>
        ))}
      </>
    );
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          minHeight: '200px'
        }}>
          <CircularProgress size={32} />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Header with Report Item Button */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1, color: 'var(--gray-900)' }}>
            Items
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {items.length} results
          </Typography>
        </Box>
        {isAuthenticated && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/create')}
            sx={{ 
              height: 'fit-content',
              px: 3,
              py: 1.5,
              fontWeight: 600
            }}
          >
            Report New Item
          </Button>
        )}
      </Box>

      {/* Clean Search and Filter Bar */}
      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'white', border: '1px solid var(--gray-200)' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search your items"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyPress={handleSearchKeyPress}
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: 'var(--gray-400)', fontSize: 20 }} />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={status}
                label="Status"
                onChange={(e) => setStatus(e.target.value as ItemStatus)}
              >
                <MenuItem value="">All Status</MenuItem>
                {Object.values(ItemStatus).map((stat) => (
                  <MenuItem key={stat} value={stat}>
                    {stat.charAt(0).toUpperCase() + stat.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Category</InputLabel>
              <Select
                value={category}
                label="Category"
                onChange={(e) => setCategory(e.target.value as ItemCategory)}
              >
                <MenuItem value="">All Categories</MenuItem>
                {Object.entries(ItemCategory).map(([key, value]) => (
                  <MenuItem key={key} value={value}>
                    {value.charAt(0).toUpperCase() + value.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Items per page</InputLabel>
              <Select
                value="25"
                label="Items per page"
              >
                <MenuItem value="25">25</MenuItem>
                <MenuItem value="50">50</MenuItem>
                <MenuItem value="100">100</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton
                onClick={() => setViewMode('grid')}
                sx={{ 
                  backgroundColor: viewMode === 'grid' ? 'var(--primary-blue)' : 'transparent',
                  border: '1px solid var(--gray-300)',
                  borderRadius: 'var(--radius-md)',
                  '&:hover': {
                    backgroundColor: viewMode === 'grid' ? 'var(--primary-blue-dark)' : 'var(--gray-100)'
                  },
                  '& .MuiSvgIcon-root': {
                    color: viewMode === 'grid' ? 'white' : 'var(--gray-500)'
                  },
                  '&:hover .MuiSvgIcon-root': {
                    color: viewMode === 'grid' ? 'white' : 'var(--gray-700)'
                  }
                }}
              >
                <ViewModule />
              </IconButton>
              <IconButton
                onClick={() => setViewMode('list')}
                sx={{ 
                  backgroundColor: viewMode === 'list' ? 'var(--primary-blue)' : 'transparent',
                  border: '1px solid var(--gray-300)',
                  borderRadius: 'var(--radius-md)',
                  '&:hover': {
                    backgroundColor: viewMode === 'list' ? 'var(--primary-blue-dark)' : 'var(--gray-100)'
                  },
                  '& .MuiSvgIcon-root': {
                    color: viewMode === 'list' ? 'white' : 'var(--gray-500)'
                  },
                  '&:hover .MuiSvgIcon-root': {
                    color: viewMode === 'list' ? 'white' : 'var(--gray-700)'
                  }
                }}
              >
                <ViewList />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="info" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Favourites Section - Only show in list view */}
      {viewMode === 'list' && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: 'var(--gray-900)' }}>
            Recent Found Items
          </Typography>
          <Paper sx={{ backgroundColor: 'white', border: '1px solid var(--gray-200)' }}>
            {items.filter(item => item.status === ItemStatus.FOUND).slice(0, 3).map((item) => (
              <ListItem
                key={item.id}
                sx={{
                  borderLeft: '4px solid var(--status-found)',
                  borderBottom: '1px solid var(--gray-100)',
                  cursor: 'pointer',
                  py: 3,
                  '&:hover': {
                    backgroundColor: 'var(--gray-50)'
                  },
                  '&:last-child': {
                    borderBottom: 'none'
                  }
                }}
                onClick={() => handleItemClick(item.id)}
              >
                <Box sx={{ display: 'flex', gap: 4, width: '100%', alignItems: 'center' }}>
                  <Box sx={{ flexShrink: 0 }}>
                    {getImageUrl(item.image_url) === '/placeholder.png' ? (
                      <Box
                        sx={{
                          width: 120,
                          height: 120,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          backgroundColor: 'var(--gray-100)',
                          borderRadius: 'var(--radius-lg)',
                          border: '2px solid var(--gray-200)'
                        }}
                      >
                        <ImageNotSupported sx={{ color: 'var(--gray-400)', fontSize: 32 }} />
                      </Box>
                    ) : (
                      <img
                        src={getImageUrl(item.image_url)}
                        alt={item.title}
                        style={{
                          width: '120px',
                          height: '120px',
                          objectFit: 'cover',
                          borderRadius: 'var(--radius-lg)',
                          border: '2px solid var(--gray-200)',
                          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                        }}
                      />
                    )}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ color: 'var(--gray-600)', fontSize: '0.75rem', mb: 0.5 }}>
                      {item.id.split('-')[0].toUpperCase()} • {item.category.toUpperCase()}
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: 'var(--gray-900)', mb: 1 }}>
                      {item.title}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Found by {item.user_name || 'Unknown'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">•</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.location_found}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">•</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(item.date_found).toLocaleDateString()}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {truncateText(item.description, 100)}
                    </Typography>
                  </Box>
                  <Box sx={{ flexShrink: 0, textAlign: 'right' }}>
                    <div className={`status-indicator status-${item.status}`}>
                      {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    </div>
                  </Box>
                </Box>
              </ListItem>
            ))}
          </Paper>
        </Box>
      )}

      {/* All Items Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: 'var(--gray-900)' }}>
          All Items ({new Date().getFullYear()})
        </Typography>
        
        {viewMode === 'list' ? (
          <Paper sx={{ backgroundColor: 'white', border: '1px solid var(--gray-200)' }}>
            {renderListView()}
          </Paper>
        ) : (
          renderGridView()
        )}
      </Box>

      {/* Clean Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(event, value) => setPage(value)}
            color="primary"
            size="medium"
          />
        </Box>
      )}
    </Container>
  );
};

export default ItemList;