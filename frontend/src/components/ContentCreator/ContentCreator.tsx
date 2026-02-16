import React from 'react';
import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { Create as CreateIcon } from '@mui/icons-material';

const ContentCreator: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Create Content
      </Typography>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <CreateIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Content Creator Coming Soon!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            The advanced content creation interface is being built. 
            You'll be able to generate AI-powered content with smart video matching here.
          </Typography>
          <Button variant="contained" disabled>
            Start Creating
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ContentCreator;