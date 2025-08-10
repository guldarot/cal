import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Paper, Grid, Card, CardContent, Button, Box, Alert, TextField, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { eventAPI, bookingAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const EventDetailPage = () => {
  const { eventUrl } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [event, setEvent] = useState(null);
  const [timeSlots, setTimeSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bookingForm, setBookingForm] = useState({
    timeSlotId: '',
    fanName: user?.name || '',
    fanEmail: user?.email || '',
    fanPhone: ''
  });
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [bookingError, setBookingError] = useState(null);

  useEffect(() => {
    fetchEventDetails();
  }, [eventUrl]);

  const fetchEventDetails = async () => {
    try {
      setLoading(true);
      // Fetch event details
      const eventResponse = await eventAPI.getPublicEvent(eventUrl);
      setEvent(eventResponse.data);
      
      // Fetch available time slots
      const slotsResponse = await eventAPI.getPublicEventSlots(eventUrl);
      setTimeSlots(slotsResponse.data.time_slots);
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch event details');
      console.error('Error fetching event details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeSlotChange = (e) => {
    setBookingForm({
      ...bookingForm,
      timeSlotId: e.target.value
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setBookingForm({
      ...bookingForm,
      [name]: value
    });
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    
    if (!bookingForm.timeSlotId) {
      setBookingError('Please select a time slot');
      return;
    }
    
    try {
      setBookingError(null);
      const bookingData = {
        time_slot_id: bookingForm.timeSlotId,
        fan_name: bookingForm.fanName,
        fan_email: bookingForm.fanEmail,
        fan_phone: bookingForm.fanPhone
      };
      
      await bookingAPI.createBooking(bookingData);
      setBookingSuccess(true);
      
      // Reset form
      setBookingForm({
        timeSlotId: '',
        fanName: user?.name || '',
        fanEmail: user?.email || '',
        fanPhone: ''
      });
      
      // Refresh time slots
      fetchEventDetails();
    } catch (err) {
      setBookingError('Failed to create booking');
      console.error('Error creating booking:', err);
    }
  };

  const handleLoginRedirect = () => {
    navigate('/login');
  };

  const handleRegisterRedirect = () => {
    navigate('/register');
  };

  if (loading) {
    return (
      <Container component="main" maxWidth="lg">
        <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
          <Typography variant="h5" align="center">
            Loading event details...
          </Typography>
        </Paper>
      </Container>
    );
  }

  if (error) {
    return (
      <Container component="main" maxWidth="lg">
        <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Paper>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="lg">
      <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
        <Typography component="h1" variant="h4" gutterBottom>
          {event?.title}
        </Typography>
        
        <Typography variant="body1" gutterBottom>
          {event?.description}
        </Typography>
        
        <Typography variant="body2" sx={{ mt: 2 }}>
          Date: {event?.event_date}
        </Typography>
        
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Available Time Slots
          </Typography>
          
          {timeSlots.length === 0 ? (
            <Typography variant="body1">
              No available time slots for this event.
            </Typography>
          ) : (
            <Grid container spacing={2}>
              {timeSlots.map((slot) => (
                <Grid item xs={12} sm={6} md={4} key={slot.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">
                        {slot.start_time} - {slot.end_time}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
        
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Book a Time Slot
          </Typography>
          
          {!isAuthenticated ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" gutterBottom>
                Please log in or register to book a time slot.
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={handleLoginRedirect}
                sx={{ mr: 2 }}
              >
                Log In
              </Button>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={handleRegisterRedirect}
              >
                Register
              </Button>
            </Box>
          ) : (
            <form onSubmit={handleBookingSubmit}>
              {bookingSuccess && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Booking created successfully!
                </Alert>
              )}
              
              {bookingError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {bookingError}
                </Alert>
              )}
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth required>
                    <InputLabel>Select Time Slot</InputLabel>
                    <Select
                      value={bookingForm.timeSlotId}
                      onChange={handleTimeSlotChange}
                      label="Select Time Slot"
                    >
                      {timeSlots.map((slot) => (
                        <MenuItem key={slot.id} value={slot.id}>
                          {slot.start_time} - {slot.end_time}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Name"
                    name="fanName"
                    value={bookingForm.fanName}
                    onChange={handleInputChange}
                    required
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    name="fanEmail"
                    type="email"
                    value={bookingForm.fanEmail}
                    onChange={handleInputChange}
                    required
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    name="fanPhone"
                    value={bookingForm.fanPhone}
                    onChange={handleInputChange}
                    required
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Button 
                    type="submit" 
                    variant="contained" 
                    color="primary"
                    fullWidth
                    size="large"
                  >
                    Book Time Slot
                  </Button>
                </Grid>
              </Grid>
            </form>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default EventDetailPage;