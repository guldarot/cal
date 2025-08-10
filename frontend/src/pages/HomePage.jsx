import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, Card, CardContent, CardActions, Button, TextField, Box, Pagination } from '@mui/material';
import { eventAPI } from '../services/api';

const HomePage = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [dateFilter, setDateFilter] = useState('');

  useEffect(() => {
    fetchEvents();
  }, [page, dateFilter]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const params = {
        page: page,
        per_page: 6,
      };
      
      if (dateFilter) {
        params.date = dateFilter;
      }
      
      const response = await eventAPI.getPublicEvents(params);
      setEvents(response.data.events);
      setTotalPages(response.data.pagination.pages);
      setError(null);
    } catch (err) {
      setError('Failed to fetch events');
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDateFilterChange = (e) => {
    setDateFilter(e.target.value);
    setPage(1); // Reset to first page when filter changes
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Loading events...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        Upcoming Events
      </Typography>
      
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
        <TextField
          label="Filter by Date"
          type="date"
          value={dateFilter}
          onChange={handleDateFilterChange}
          InputLabelProps={{
            shrink: true,
          }}
          sx={{ width: 300 }}
        />
      </Box>
      
      {error && (
        <Typography color="error" align="center" gutterBottom>
          {error}
        </Typography>
      )}
      
      <Grid container spacing={3}>
        {events.map((event) => (
          <Grid item xs={12} sm={6} md={4} key={event.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  {event.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {event.description}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Date: {event.event_date}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  component="a" 
                  href={`/events/${event.unique_url}`}
                >
                  View Details
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {events.length === 0 && !loading && (
        <Typography variant="h6" align="center" sx={{ mt: 4 }}>
          No events found
        </Typography>
      )}
      
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Pagination 
          count={totalPages} 
          page={page} 
          onChange={handlePageChange} 
          color="primary" 
        />
      </Box>
    </Container>
  );
};

export default HomePage;