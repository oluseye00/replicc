import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Folder as FolderIcon } from '@mui/icons-material';

const ContentLibrary: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Content Library
      </Typography>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <FolderIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Content Library Coming Soon!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Your generated content and video matches will appear here.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ContentLibrary;