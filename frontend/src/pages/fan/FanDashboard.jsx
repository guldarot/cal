import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Grid, Card, CardContent, CardActions, Button, Box } from '@mui/material';
import { bookingAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const FanDashboard = () => {
  const [bookingsCount, setBookingsCount] = useState(0);
  const [upcomingBookingsCount, setUpcomingBookingsCount] = useState(0);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch bookings for this fan
      const bookingsResponse = await bookingAPI.getUserBookings();
      setBookingsCount(bookingsResponse.data.pagination.total);
      
      // Count upcoming bookings (simplified check)
      let upcomingCount = 0;
      bookingsResponse.data.bookings.forEach(booking => {
        // In a real app, you would check if the event date is in the future
        upcomingCount++;
      });
      
      setUpcomingBookingsCount(upcomingCount);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    }
  };

  const handleBrowseEvents = () => {
    navigate('/');
  };

  const handleViewBookings = () => {
    navigate('/fan/bookings');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Fan Dashboard
      </Typography>
      
      <Typography variant="h6" gutterBottom>
        Welcome, {user?.name}!
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                {bookingsCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Bookings Made
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                {upcomingBookingsCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upcoming Bookings
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
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  Browse Events
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Find and book appointments
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={handleBrowseEvents}>
                  Browse
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  My Bookings
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View and manage your bookings
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

export default FanDashboard;