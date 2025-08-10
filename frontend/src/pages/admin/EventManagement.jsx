import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Grid, Card, CardContent, CardActions, Button, Box, Pagination, TextField, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { eventAPI } from '../../services/api';

const EventManagement = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filter, setFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    fetchEvents();
  }, [page, filter]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const params = {
        page: page,
        per_page: 6,
      };
      
      if (filter !== 'all') {
        params.is_published = filter === 'published';
      }
      
      const response = await eventAPI.getAdminEvents(params);
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

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleFilterChange = (e) => {
    setFilter(e.target.value);
    setPage(1); // Reset to first page when filter changes
  };

  const handleCreateEvent = () => {
    navigate('/admin/events/create');
  };

  const handleEditEvent = (eventId) => {
    navigate(`/admin/events/${eventId}/edit`);
  };

  const handleViewBookings = (eventId) => {
    navigate(`/admin/events/${eventId}/bookings`);
  };

  const handlePublishToggle = async (eventId, currentStatus) => {
    try {
      await eventAPI.publishEvent(eventId, { is_published: !currentStatus });
      // Refresh the events list
      fetchEvents();
    } catch (err) {
      setError('Failed to update event status');
      console.error('Error updating event status:', err);
    }
  };

  const handleDeleteEvent = async (eventId) => {
    if (window.confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
      try {
        await eventAPI.deleteEvent(eventId);
        // Refresh the events list
        fetchEvents();
      } catch (err) {
        setError('Failed to delete event');
        console.error('Error deleting event:', err);
      }
    }
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Manage Events
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleCreateEvent}
        >
          Create Event
        </Button>
      </Box>
      
      {error && (
        <Typography color="error" align="center" gutterBottom>
          {error}
        </Typography>
      )}
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Status</InputLabel>
          <Select
            value={filter}
            label="Filter by Status"
            onChange={handleFilterChange}
          >
            <MenuItem value="all">All Events</MenuItem>
            <MenuItem value="published">Published</MenuItem>
            <MenuItem value="draft">Draft</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
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
                <Typography variant="body2">
                  Status: {event.is_published ? 'Published' : 'Draft'}
                </Typography>
                <Typography variant="body2">
                  Bookings: {event.bookings_count || 0}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => handleEditEvent(event.id)}>
                  Edit
                </Button>
                <Button size="small" onClick={() => handleViewBookings(event.id)}>
                  Bookings
                </Button>
                <Button 
                  size="small" 
                  onClick={() => handlePublishToggle(event.id, event.is_published)}
                >
                  {event.is_published ? 'Unpublish' : 'Publish'}
                </Button>
                <Button 
                  size="small" 
                  color="error" 
                  onClick={() => handleDeleteEvent(event.id)}
                >
                  Delete
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

export default EventManagement;