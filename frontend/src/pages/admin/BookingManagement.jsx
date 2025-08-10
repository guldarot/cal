import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Box, Alert, Pagination, CircularProgress } from '@mui/material';
import { eventAPI } from '../../services/api';

const BookingManagement = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    fetchBookings();
  }, [page]);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await eventAPI.getAdminBookings({ page, per_page: 10 });
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

  const handleBackToDashboard = () => {
    navigate('/admin/dashboard');
  };

  if (loading && bookings.length === 0) {
    return (
      <Container component="main" maxWidth="lg">
        <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
            <CircularProgress />
          </Box>
        </Paper>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="lg">
      <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography component="h1" variant="h5">
            All Bookings
          </Typography>
          <Button
            variant="outlined"
            onClick={handleBackToDashboard}
          >
            Back to Dashboard
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {bookings.length === 0 ? (
          <Typography variant="h6" align="center" sx={{ mt: 4 }}>
            No bookings found
          </Typography>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Event</TableCell>
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
                      <TableCell>{booking.event.title}</TableCell>
                      <TableCell>{booking.fan_name}</TableCell>
                      <TableCell>{booking.fan_email}</TableCell>
                      <TableCell>{booking.fan_phone}</TableCell>
                      <TableCell>
                        {booking.time_slot.start_time} - {booking.time_slot.end_time}
                      </TableCell>
                      <TableCell>
                        {new Date(booking.created_at).toLocaleString()}
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

export default BookingManagement;