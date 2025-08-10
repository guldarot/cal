import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, TextField, Button, Box, Paper, Alert, Grid, IconButton } from '@mui/material';
import { eventAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';

const EditEventPage = () => {
  const { id } = useParams();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_date: '',
    time_slots: []
  });
  const [originalTimeSlots, setOriginalTimeSlots] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    fetchEventDetails();
  }, [id]);

  const fetchEventDetails = async () => {
    try {
      const response = await eventAPI.getEvent(id);
      const event = response.data;
      
      setFormData({
        title: event.title,
        description: event.description,
        event_date: event.event_date,
        time_slots: event.time_slots.map(slot => ({
          id: slot.id,
          start_time: slot.start_time,
          end_time: slot.end_time
        }))
      });
      
      setOriginalTimeSlots(event.time_slots);
      setError('');
    } catch (err) {
      setError('Failed to fetch event details');
      console.error('Error fetching event details:', err);
    } finally {
      setLoading(false);
    }
  };

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
    const slot = formData.time_slots[index];
    
    // If this is an existing slot (has an id), we need to mark it for deletion
    if (slot.id) {
      const newTimeSlots = [...formData.time_slots];
      newTimeSlots[index].deleted = true;
      setFormData(prev => ({
        ...prev,
        time_slots: newTimeSlots
      }));
    } else {
      // If it's a new slot, just remove it from the array
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
    setSaving(true);

    try {
      // Prepare data for update
      const updateData = {
        title: formData.title,
        description: formData.description,
        event_date: formData.event_date
      };

      await eventAPI.updateEvent(id, updateData);
      
      // For simplicity, we're not handling time slot updates in this example
      // In a real application, you would need to handle time slot updates/deletions separately
      
      // Redirect to event management page after successful update
      navigate('/admin/events');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update event. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Container component="main" maxWidth="md">
        <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
          <Typography variant="h5" align="center">
            Loading event details...
          </Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="md">
      <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
        <Typography component="h1" variant="h5" align="center" gutterBottom>
          Edit Event
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
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
            // Don't show deleted slots
            !slot.deleted && (
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
                  >
                    <RemoveIcon />
                  </IconButton>
                </Grid>
              </Grid>
            )
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
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default EditEventPage;