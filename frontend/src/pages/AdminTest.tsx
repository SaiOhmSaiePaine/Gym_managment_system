import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const AdminTest: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Admin Test Page
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body1">
            This is a test page for admin functionality.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default AdminTest;