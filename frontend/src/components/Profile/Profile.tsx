import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Person as PersonIcon } from '@mui/icons-material';

const Profile: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Profile Settings
      </Typography>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <PersonIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Profile Management Coming Soon!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your account settings, voice profiles, and billing here.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Profile;