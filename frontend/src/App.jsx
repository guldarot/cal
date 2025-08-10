import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import EventDetailPage from './pages/EventDetailPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import EventManagement from './pages/admin/EventManagement';
import BookingManagement from './pages/admin/BookingManagement';
import FanDashboard from './pages/fan/FanDashboard';
import BookingHistory from './pages/fan/BookingHistory';
import CreateEventPage from './pages/admin/CreateEventPage';
import EditEventPage from './pages/admin/EditEventPage';
import EventBookingsPage from './pages/admin/EventBookingsPage';
import { AuthProvider } from './context/AuthContext';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Header />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/events/:eventUrl" element={<EventDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Admin routes */}
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/events" element={<EventManagement />} />
            <Route path="/admin/events/create" element={<CreateEventPage />} />
            <Route path="/admin/events/:id/edit" element={<EditEventPage />} />
            <Route path="/admin/events/:id/bookings" element={<EventBookingsPage />} />
            <Route path="/admin/bookings" element={<BookingManagement />} />
            
            {/* Fan routes */}
            <Route path="/fan/dashboard" element={<FanDashboard />} />
            <Route path="/fan/bookings" element={<BookingHistory />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
