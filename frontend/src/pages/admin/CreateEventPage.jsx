import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, TextField, Button, Box, Paper, Alert, Grid, IconButton } from '@mui/material';
import { eventAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';

const CreateEventPage = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_date: '',
    time_slots: [{ start_time: '', end_time: '' }]
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTimeSlotChange = (index, field, value) => {
    const newTimeSlots = [...formData.time_slots];
    newTimeSlots[index][field] = value;
    setFormData(prev => ({
      ...prev,
      time_slots: newTimeSlots
    }));
  };

  const addTimeSlot = () => {
    setFormData(prev => ({
      ...prev,
      time_slots: [...prev.time_slots, { start_time: '', end_time: '' }]
    }));
  };

  const removeTimeSlot = (index) => {
    if (formData.time_slots.length > 1) {
      const newTimeSlots = formData.time_slots.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        time_slots: newTimeSlots
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    // Validate that all time slots have values
    const hasEmptySlots = formData.time_slots.some(
      slot => !slot.start_time || !slot.end_time
    );
    
    if (hasEmptySlots) {
      setError('Please fill in all time slots or remove empty ones.');
      setLoading(false);
      return;
    }

    try {
      await eventAPI.createEvent(formData);
      setSuccess(true);
      // Redirect to event management page after successful creation
      setTimeout(() => {
        navigate('/admin/events');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create event. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
        <Typography component="h1" variant="h5" align="center" gutterBottom>
          Create New Event
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Event created successfully!
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="title"
            label="Event Title"
            name="title"
            value={formData.title}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="description"
            label="Event Description"
            name="description"
            multiline
            rows={4}
            value={formData.description}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="event_date"
            label="Event Date"
            name="event_date"
            type="date"
            InputLabelProps={{
              shrink: true,
            }}
            value={formData.event_date}
            onChange={handleChange}
          />
          
          <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
            Time Slots
          </Typography>
          
          {formData.time_slots.map((slot, index) => (
            <Grid container spacing={2} key={index} sx={{ mb: 2 }}>
              <Grid item xs={5}>
                <TextField
                  required
                  fullWidth
                  label="Start Time"
                  type="time"
                  InputLabelProps={{
                    shrink: true,
                  }}
                  value={slot.start_time}
                  onChange={(e) => handleTimeSlotChange(index, 'start_time', e.target.value)}
                />
              </Grid>
              <Grid item xs={5}>
                <TextField
                  required
                  fullWidth
                  label="End Time"
                  type="time"
                  InputLabelProps={{
                    shrink: true,
                  }}
                  value={slot.end_time}
                  onChange={(e) => handleTimeSlotChange(index, 'end_time', e.target.value)}
                />
              </Grid>
              <Grid item xs={2}>
                <IconButton
                  onClick={() => removeTimeSlot(index)}
                  disabled={formData.time_slots.length <= 1}
                >
                  <RemoveIcon />
                </IconButton>
              </Grid>
            </Grid>
          ))}
          
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={addTimeSlot}
            sx={{ mb: 2 }}
          >
            Add Time Slot
          </Button>
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Event'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default CreateEventPage;