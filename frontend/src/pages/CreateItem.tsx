import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  CircularProgress,
} from '@mui/material';
import { ArrowBack, Add, CloudUpload } from '@mui/icons-material';
import { ItemStatus, ItemCategory } from '../types/item';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const CreateItem = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const [loading, setLoading] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/auth', { state: { from: '/create' } });
    }
  }, [isAuthenticated, isLoading, navigate]);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: ItemCategory.OTHER,
    status: ItemStatus.FOUND,
    location_found: '',
    date_found: new Date().toISOString().split('T')[0], // Today's date
    image_url: '',
  });

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (formErrors[field]) {
      setFormErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file (JPG, PNG, etc.)');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image file size must be less than 5MB');
        return;
      }
      
      setSelectedFile(file);
      setError(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    // Title is optional - if empty, we'll auto-generate from description
    
    if (!formData.description.trim()) {
      errors.description = 'Description is required';
    }
    
    if (!formData.location_found.trim()) {
      errors.location_found = 'Location is required';
    }
    
    if (!formData.date_found) {
      errors.date_found = 'Date is required';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setUploadingImage(!!selectedFile);
    setError(null);

    try {
      // Auto-generate title from description if title is empty
      let finalTitle = formData.title.trim();
      if (!finalTitle && formData.description.trim()) {
        // Take first 50 characters of description as title
        finalTitle = formData.description.trim().substring(0, 50);
        if (formData.description.length > 50) {
          finalTitle += '...';
        }
      }
      if (!finalTitle) {
        finalTitle = formData.status === ItemStatus.LOST ? 'Lost Item' : 'Found Item';
      }

      // Use different submission strategies based on whether an image is selected
      let response;
      
      if (selectedFile) {
        // Use multipart form data when image is selected
      const submitFormData = new FormData();
        submitFormData.append('title', finalTitle);
      submitFormData.append('description', formData.description);
      submitFormData.append('category', formData.category);
      submitFormData.append('status', formData.status);
      submitFormData.append('location_found', formData.location_found);
      submitFormData.append('date_found', formData.date_found);
        submitFormData.append('image', selectedFile);

        response = await api.post('/api/items', submitFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 60000, // 60 second timeout for item creation (includes file upload)
        });
      } else {
        // Use JSON when no image is selected (faster and more reliable)
        const jsonData = {
          title: finalTitle,
          description: formData.description,
          category: formData.category,
          status: formData.status,
          location: formData.location_found,
          date_found: formData.date_found,
        };

        response = await api.post('/api/items', jsonData, {
        headers: {
            'Content-Type': 'application/json'
          },
          timeout: 30000, // 30 second timeout for JSON submission
        });
      }

      // Axios returns the data directly
      const createdItem = response.data;
      console.log('Item created:', createdItem);
      
      setSuccess(true);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        category: ItemCategory.OTHER,
        status: ItemStatus.FOUND,
        location_found: '',
        date_found: new Date().toISOString().split('T')[0],
        image_url: '',
      });
      setSelectedFile(null);
      setImagePreview(null);

      // Redirect to main page after 2 seconds
      setTimeout(() => {
        navigate('/');
      }, 2000);

    } catch (err: any) {
      console.error('Failed to create item:', err);
      setError(err.response?.data?.error || err.message || 'Failed to create item. Please try again.');
    } finally {
      setLoading(false);
      setUploadingImage(false);
    }
  };

  const handleBackClick = () => {
    navigate('/');
  };

  if (success) {
    return (
      <Container>
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Alert severity="success" sx={{ mb: 2 }}>
            ✅ {formData.status === ItemStatus.LOST ? 'Lost item reported successfully!' : 'Found item reported successfully!'} 
            {selectedFile && ' Image uploaded. '}
            Redirecting...
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Button 
          onClick={handleBackClick} 
          startIcon={<ArrowBack />}
          sx={{ mb: 3 }}
        >
          Back to Items
        </Button>

        <Paper elevation={2} sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <Add sx={{ mr: 1 }} />
            Report Item
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Help reunite lost items with their owners by reporting what you've found or lost.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Item Title (Optional)"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  error={!!formErrors.title}
                  helperText={formErrors.title || "Leave empty to auto-generate from description"}
                  placeholder="e.g., Lost iPhone 13, Found Car Keys"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  error={!!formErrors.description}
                  helperText={formErrors.description}
                  placeholder="Provide details about the item - color, brand, condition, any distinctive features..."
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={formData.category}
                    label="Category"
                    onChange={(e) => handleInputChange('category', e.target.value)}
                  >
                    <MenuItem value={ItemCategory.ELECTRONICS}>Electronics</MenuItem>
                    <MenuItem value={ItemCategory.ACCESSORIES}>Accessories</MenuItem>
                    <MenuItem value={ItemCategory.BOOKS}>Books</MenuItem>
                    <MenuItem value={ItemCategory.CLOTHING}>Clothing</MenuItem>
                    <MenuItem value={ItemCategory.OTHER}>Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    label="Status"
                    onChange={(e) => handleInputChange('status', e.target.value)}
                  >
                    <MenuItem value={ItemStatus.FOUND}>Found</MenuItem>
                    <MenuItem value={ItemStatus.LOST}>Lost</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={formData.status === ItemStatus.LOST ? "Location Lost" : "Location Found"}
                  value={formData.location_found}
                  onChange={(e) => handleInputChange('location_found', e.target.value)}
                  error={!!formErrors.location_found}
                  helperText={formErrors.location_found}
                  placeholder={formData.status === ItemStatus.LOST ? "e.g., Last seen at Library 2nd Floor" : "e.g., Found at Library 2nd Floor"}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label={formData.status === ItemStatus.LOST ? "Date Lost" : "Date Found"}
                  value={formData.date_found}
                  onChange={(e) => handleInputChange('date_found', e.target.value)}
                  error={!!formErrors.date_found}
                  helperText={formErrors.date_found}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>

              {/* File Upload Section */}
              <Grid item xs={12}>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Item Photo (Optional)
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Upload a photo to help identify the item. Supports JPG, PNG files up to 5MB.
                  </Typography>
                  
                  <input
                    accept="image/*"
                    style={{ display: 'none' }}
                    id="image-upload"
                    type="file"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="image-upload">
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<CloudUpload />}
                      disabled={loading}
                    >
                      Choose Image
                    </Button>
                  </label>
                  
                  {selectedFile && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                    </Typography>
                  )}
                  
                  {imagePreview && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" gutterBottom>Preview:</Typography>
                      <img 
                        src={imagePreview} 
                        alt="Preview" 
                        style={{ 
                          maxWidth: '200px', 
                          maxHeight: '200px', 
                          objectFit: 'cover',
                          borderRadius: '8px',
                          border: '1px solid #ddd'
                        }} 
                      />
                    </Box>
                  )}
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button 
                    onClick={handleBackClick}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <Add />}
                  >
                    {loading ? (uploadingImage ? 'Uploading Image...' : 'Reporting...') : 'Report Item'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default CreateItem;