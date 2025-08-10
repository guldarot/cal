import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Box, Alert, Pagination } from '@mui/material';
import { eventAPI } from '../../services/api';

const EventBookingsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchEventDetails();
    fetchBookings();
  }, [id, page]);

  const fetchEventDetails = async () => {
    try {
      const response = await eventAPI.getEvent(id);
      setEvent(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch event details');
      console.error('Error fetching event details:', err);
    }
  };

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const params = {
        page: page,
        per_page: 10
      };
      
      const response = await eventAPI.getEventBookings(id, params);
      setBookings(response.data.bookings);
      setTotalPages(response.data.pagination.pages);
      setError(null);
    } catch (err) {
      setError('Failed to fetch bookings');
      console.error('Error fetching bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleBackToEvents = () => {
    navigate('/admin/events');
  };

  if (loading && !event) {
    return (
      <Container component="main" maxWidth="md">
        <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
          <Typography variant="h5" align="center">
            Loading event bookings...
          </Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="lg">
      <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography component="h1" variant="h5">
            Bookings for {event?.title}
          </Typography>
          <Button 
            variant="outlined" 
            onClick={handleBackToEvents}
          >
            Back to Events
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {bookings.length === 0 && !loading ? (
          <Typography variant="h6" align="center" sx={{ mt: 4 }}>
            No bookings found for this event
          </Typography>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Fan Name</TableCell>
                    <TableCell>Fan Email</TableCell>
                    <TableCell>Fan Phone</TableCell>
                    <TableCell>Time Slot</TableCell>
                    <TableCell>Booking Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {bookings.map((booking) => (
                    <TableRow key={booking.id}>
                      <TableCell>{booking.fan_name}</TableCell>
                      <TableCell>{booking.fan_email}</TableCell>
                      <TableCell>{booking.fan_phone}</TableCell>
                      <TableCell>
                        {booking.time_slot.start_time} - {booking.time_slot.end_time}
                      </TableCell>
                      <TableCell>
                        {new Date(booking.created_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination 
                count={totalPages} 
                page={page} 
                onChange={handlePageChange} 
                color="primary" 
              />
            </Box>
          </>
        )}
      </Paper>
    </Container>
  );
};

export default EventBookingsPage;