import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  IconButton,
} from '@mui/material';
import {
  Create as CreateIcon,
  VideoLibrary as VideoIcon,
  AutoAwesome as MagicIcon,
  TrendingUp as TrendingIcon,
  Article as ArticleIcon,
  VideoCall as VideoCallIcon,
  Link as LinkIcon,
  MoreVert as MoreVertIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { contentAPI, ContentItem } from '../../services/api';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  trend?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, trend }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
  >
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight="bold" color={color}>
              {value}
            </Typography>
            {trend && (
              <Chip
                label={trend}
                size="small"
                color="success"
                variant="outlined"
                sx={{ mt: 1 }}
              />
            )}
          </Box>
          <Avatar
            sx={{
              bgcolor: `${color}.light`,
              color: `${color}.main`,
              width: 56,
              height: 56,
            }}
          >
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  </motion.div>
);

interface QuickActionProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  onClick: () => void;
}

const QuickAction: React.FC<QuickActionProps> = ({ title, description, icon, color, onClick }) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
  >
    <Card 
      sx={{ 
        height: '100%', 
        cursor: 'pointer',
        '&:hover': { boxShadow: 3 },
        transition: 'box-shadow 0.2s',
      }}
      onClick={onClick}
    >
      <CardContent sx={{ textAlign: 'center', py: 3 }}>
        <Avatar
          sx={{
            bgcolor: `${color}.light`,
            color: `${color}.main`,
            width: 64,
            height: 64,
            mx: 'auto',
            mb: 2,
          }}
        >
          {icon}
        </Avatar>
        <Typography variant="h6" fontWeight="600" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
    </Card>
  </motion.div>
);

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [recentContent, setRecentContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecentContent();
  }, []);

  const loadRecentContent = async () => {
    try {
      const response = await contentAPI.list({ limit: 5 });
      setRecentContent(response.data.results || []);
    } catch (error) {
      console.error('Failed to load recent content:', error);
      // Mock data for demo purposes
      setRecentContent([
        {
          id: '1',
          title: '5 Productivity Tips for Remote Workers',
          content: 'Generated content for social media...',
          content_type: 'social',
          platforms: ['tiktok', 'instagram', 'linkedin'],
          created_at: '2024-02-07T10:00:00Z',
          match_score: 92,
        },
        {
          id: '2',
          title: 'AI in Business: The Future is Now',
          content: 'YouTube video script content...',
          content_type: 'video',
          platforms: ['youtube'],
          created_at: '2024-02-06T15:30:00Z',
          match_score: 89,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case 'social':
        return <MagicIcon />;
      case 'video':
        return <VideoCallIcon />;
      case 'blog':
        return <ArticleIcon />;
      default:
        return <CreateIcon />;
    }
  };

  const getContentTypeColor = (type: string) => {
    switch (type) {
      case 'social':
        return 'primary';
      case 'video':
        return 'secondary';
      case 'blog':
        return 'success';
      default:
        return 'info';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Welcome back! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your content creation today.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          flexWrap: 'wrap',
          gap: 3,
          mb: 4,
        }}
      >
        <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
          <StatCard
            title="Content Generated"
            value={12}
            icon={<CreateIcon />}
            color="primary"
            trend="+23% this week"
          />
        </Box>
        <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
          <StatCard
            title="Videos Uploaded"
            value={8}
            icon={<VideoIcon />}
            color="secondary"
            trend="+2 this week"
          />
        </Box>
        <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
          <StatCard
            title="Perfect Matches"
            value={23}
            icon={<LinkIcon />}
            color="success"
            trend="94% avg score"
          />
        </Box>
        <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
          <StatCard
            title="Engagement"
            value="2.4k"
            icon={<TrendingIcon />}
            color="warning"
            trend="+15% this month"
          />
        </Box>
      </Box>

      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          gap: 3,
        }}
      >
        {/* Quick Actions */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 50%' } }}>
          <Typography variant="h6" fontWeight="600" gutterBottom>
            Quick Actions
          </Typography>
          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 2,
            }}
          >
            <Box sx={{ flex: '1 1 calc(50% - 8px)', minWidth: 140 }}>
              <QuickAction
                title="Social Media"
                description="Multi-platform posts"
                icon={<MagicIcon />}
                color="primary"
                onClick={() => navigate('/create?type=social')}
              />
            </Box>
            <Box sx={{ flex: '1 1 calc(50% - 8px)', minWidth: 140 }}>
              <QuickAction
                title="Video Script"
                description="With smart matching"
                icon={<VideoCallIcon />}
                color="secondary"
                onClick={() => navigate('/create?type=video')}
              />
            </Box>
            <Box sx={{ flex: '1 1 calc(50% - 8px)', minWidth: 140 }}>
              <QuickAction
                title="Blog Post"
                description="Long-form content"
                icon={<ArticleIcon />}
                color="success"
                onClick={() => navigate('/create?type=blog')}
              />
            </Box>
            <Box sx={{ flex: '1 1 calc(50% - 8px)', minWidth: 140 }}>
              <QuickAction
                title="Upload Video"
                description="Add to your library"
                icon={<AddIcon />}
                color="info"
                onClick={() => navigate('/library')}
              />
            </Box>
          </Box>
        </Box>

        {/* Recent Content */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 50%' } }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight="600">
              Recent Content
            </Typography>
            <Button
              variant="text"
              size="small"
              onClick={() => navigate('/library')}
            >
              View All
            </Button>
          </Box>
          
          <Card>
            <CardContent sx={{ p: 0 }}>
              {loading ? (
                <Box sx={{ p: 3 }}>
                  <LinearProgress />
                </Box>
              ) : recentContent.length === 0 ? (
                <Box sx={{ p: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary">
                    No content yet. Create your first piece!
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<CreateIcon />}
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/create')}
                  >
                    Create Content
                  </Button>
                </Box>
              ) : (
                <List sx={{ py: 0 }}>
                  {recentContent.map((item, index) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <ListItem
                        divider={index < recentContent.length - 1}
                        secondaryAction={
                          <IconButton edge="end" size="small">
                            <MoreVertIcon />
                          </IconButton>
                        }
                        sx={{
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'action.hover' },
                        }}
                        onClick={() => navigate(`/library?content=${item.id}`)}
                      >
                        <ListItemIcon>
                          <Avatar
                            sx={{
                              bgcolor: `${getContentTypeColor(item.content_type)}.light`,
                              color: `${getContentTypeColor(item.content_type)}.main`,
                              width: 40,
                              height: 40,
                            }}
                          >
                            {getContentTypeIcon(item.content_type)}
                          </Avatar>
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography variant="subtitle2" fontWeight="600">
                              {item.title}
                            </Typography>
                          }
                          secondary={
                            <Box sx={{ mt: 0.5 }}>
                              <Box sx={{ display: 'flex', gap: 1, mb: 0.5 }}>
                                <Chip
                                  label={item.content_type}
                                  size="small"
                                  color={getContentTypeColor(item.content_type) as any}
                                  variant="outlined"
                                />
                                {item.match_score && (
                                  <Chip
                                    label={`${item.match_score}% match`}
                                    size="small"
                                    color="success"
                                    variant="outlined"
                                  />
                                )}
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                {formatDate(item.created_at)} • {item.platforms.join(', ')}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    </motion.div>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Usage Overview */}
      <Box sx={{ mt: 2 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight="600" gutterBottom>
              Usage Overview - Starter Plan
            </Typography>
            <Box
              sx={{
                display: 'flex',
                flexDirection: { xs: 'column', md: 'row' },
                gap: 3,
              }}
            >
              <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Content Generated
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" fontWeight="600" sx={{ mr: 2 }}>
                      12 / 100
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      (88 remaining)
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={12}
                    sx={{ height: 8, borderRadius: 1 }}
                  />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Videos Uploaded
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" fontWeight="600" sx={{ mr: 2 }}>
                      8 / 50
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      (42 remaining)
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={16}
                    color="secondary"
                    sx={{ height: 8, borderRadius: 1 }}
                  />
                </Box>
            </Box>
              <Button
                variant="outlined"
                color="primary"
                sx={{ mt: 3 }}
                onClick={() => navigate('/upgrade')}
              >
                Upgrade Plan
              </Button>
            </CardContent>
          </Card>
      </Box>
    </Box>
  );
};

export default Dashboard;