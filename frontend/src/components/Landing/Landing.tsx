import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Avatar,
} from '@mui/material';
import {
  AutoAwesome as MagicIcon,
  Share as ShareIcon,
  VideoLibrary as VideoIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Landing: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <MagicIcon />,
      title: 'Smart AI Matching',
      description: '92% accuracy in video-content pairing with intelligent AI analysis',
      color: 'primary',
    },
    {
      icon: <ShareIcon />,
      title: 'Multi-Platform Content',
      description: 'Optimized for TikTok, Instagram, LinkedIn, YouTube and more',
      color: 'secondary',
    },
    {
      icon: <VideoIcon />,
      title: 'Video Intelligence',
      description: 'Automatic video analysis for mood, pace, style and optimization',
      color: 'success',
    },
    {
      icon: <TrendingIcon />,
      title: '5x Faster Creation',
      description: 'Create professional content in minutes instead of hours',
      color: 'warning',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: 12,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Box sx={{ mb: 4 }}>
              <MagicIcon sx={{ fontSize: 80, mb: 2 }} />
              <Typography variant="h2" fontWeight="bold" gutterBottom>
                Repli
              </Typography>
            </Box>
            
            <Typography variant="h3" fontWeight="600" gutterBottom sx={{ mb: 3 }}>
              AI-Powered Content Creation
              <br />
              <span style={{ color: '#FFE082' }}>Meets Smart Video Matching</span>
            </Typography>
            
            <Typography variant="h6" sx={{ mb: 6, opacity: 0.9, maxWidth: '800px', mx: 'auto' }}>
              Transform your content creation with intelligent AI that analyzes your style, 
              generates multi-platform content, and automatically matches your videos 
              for perfect content packages.
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                sx={{
                  bgcolor: 'white',
                  color: 'primary.main',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  '&:hover': { bgcolor: 'grey.100' },
                }}
                onClick={() => navigate('/register')}
              >
                Start Creating Free
              </Button>
              <Button
                variant="outlined"
                size="large"
                sx={{
                  borderColor: 'white',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  '&:hover': {
                    borderColor: 'white',
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
                onClick={() => navigate('/login')}
              >
                Sign In
              </Button>
            </Box>
          </motion.div>
        </Container>
      </Box>

      {/* Stats Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', md: 'row' },
              textAlign: 'center',
              gap: 4,
              mb: 8,
            }}
          >
            <Box sx={{ flex: 1 }}>
              <Typography variant="h3" fontWeight="bold" color="primary.main" gutterBottom>
                92%
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Match Accuracy
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h3" fontWeight="bold" color="secondary.main" gutterBottom>
                5 min
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Average Creation Time
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h3" fontWeight="bold" color="success.main" gutterBottom>
                5x
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Faster Than Manual
              </Typography>
            </Box>
          </Box>
        </motion.div>
      </Container>

      {/* Features Section */}
      <Box sx={{ bgcolor: 'grey.50', py: 8 }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <Typography variant="h3" fontWeight="bold" textAlign="center" gutterBottom>
              Why Choose Repli?
            </Typography>
            <Typography
              variant="h6"
              textAlign="center"
              color="text.secondary"
              sx={{ mb: 6, maxWidth: '600px', mx: 'auto' }}
            >
              Stop spending hours creating content and matching videos. 
              Let AI do the heavy lifting while you focus on what matters most.
            </Typography>
            
            <Box
              sx={{
                display: 'flex',
                flexDirection: { xs: 'column', sm: 'row' },
                flexWrap: 'wrap',
                gap: 4,
              }}
            >
              {features.map((feature, index) => (
                <Box
                  key={index}
                  sx={{
                    flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 16px)', md: '1 1 calc(25% - 24px)' },
                    minWidth: 0,
                  }}
                >
                  <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 * index }}
                  >
                    <Card sx={{ height: '100%', textAlign: 'center' }}>
                      <CardContent sx={{ p: 4 }}>
                        <Avatar
                          sx={{
                            bgcolor: `${feature.color}.light`,
                            color: `${feature.color}.main`,
                            width: 64,
                            height: 64,
                            mx: 'auto',
                            mb: 3,
                          }}
                        >
                          {feature.icon}
                        </Avatar>
                        <Typography variant="h6" fontWeight="600" gutterBottom>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {feature.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Box>
              ))}
            </Box>
          </motion.div>
        </Container>
      </Box>

      {/* CTA Section */}
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Ready to Transform Your Content Creation?
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
            Join thousands of creators who are already using AI to create amazing content
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            sx={{
              px: 6,
              py: 2,
              fontSize: '1.2rem',
              fontWeight: 600,
            }}
            onClick={() => navigate('/register')}
          >
            Get Started Free - No Credit Card Required
          </Button>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            ✨ 10 free content generations • 🎬 5 video uploads • 🚀 Smart AI matching
          </Typography>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Landing;