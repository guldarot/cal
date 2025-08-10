import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Grid, Card, CardContent, CardActions, Button, Box } from '@mui/material';
import { eventAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const AdminDashboard = () => {
  const [eventsCount, setEventsCount] = useState(0);
  const [bookingsCount, setBookingsCount] = useState(0);
  const [upcomingEventsCount, setUpcomingEventsCount] = useState(0);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch events for this admin
      const eventsResponse = await eventAPI.getAdminEvents();
      setEventsCount(eventsResponse.data.pagination.total);
      
      // For simplicity, we'll just count the events as bookings
      // In a real app, you would fetch actual booking data
      let totalBookings = 0;
      let upcomingEvents = 0;
      
      // Count bookings and upcoming events
      eventsResponse.data.events.forEach(event => {
        totalBookings += event.bookings_count || 0;
        // Check if event is upcoming (this is a simplified check)
        if (event.is_published) {
          upcomingEvents++;
        }
      });
      
      setBookingsCount(totalBookings);
      setUpcomingEventsCount(upcomingEvents);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    }
  };

  const handleCreateEvent = () => {
    navigate('/admin/events/create');
  };

  const handleManageEvents = () => {
    navigate('/admin/events');
  };

  const handleViewBookings = () => {
    navigate('/admin/bookings');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      
      <Typography variant="h6" gutterBottom>
        Welcome, {user?.name}!
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                {eventsCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Events Created
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                {bookingsCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Bookings Received
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                {upcomingEventsCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upcoming Events
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  Create Event
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create a new event with time slots
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={handleCreateEvent}>
                  Create
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  Manage Events
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View and edit your events
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={handleManageEvents}>
                  Manage
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  View Bookings
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  See all bookings for your events
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={handleViewBookings}>
                  View
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default AdminDashboard;