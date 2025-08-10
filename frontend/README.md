# Appointment Booking System - Frontend

This is the frontend application for the Appointment Booking System, built with React and Material-UI.

## Features

- User authentication (login/register)
- Role-based access control (admin/fan)
- Event browsing and searching
- Appointment booking
- Admin dashboard for event and booking management
- Fan dashboard for booking history

## Technologies Used

- React.js
- React Router
- Material-UI (MUI)
- Axios for API requests
- Vite as the build tool

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

## Getting Started

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```
4. Start the development server:
   ```
   npm run dev
   ```

The application will be available at http://localhost:5173

## Building for Production

To create a production build:

```
npm run build
```

The build files will be generated in the `dist` directory.

## Deployment

The frontend can be deployed to any static hosting service such as:

- Vercel
- Netlify
- GitHub Pages
- AWS S3

## Project Structure

```
src/
├── components/          # Reusable UI components
├── context/            # React context providers
├── pages/              # Page components
│   ├── admin/          # Admin-specific pages
│   └── fan/            # Fan-specific pages
├── services/           # API service functions
├── App.jsx             # Main app component
└── main.jsx            # Entry point
```

## Available Scripts

- `npm run dev` - Starts the development server
- `npm run build` - Builds the app for production
- `npm run preview` - Previews the production build locally
- `npm run lint` - Runs ESLint

## Environment Variables

The frontend application uses the following environment variables:

- `VITE_API_URL` - The base URL for the backend API (default: http://localhost:5000/api)

To set environment variables, create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:5000/api
```

## Development

To run the development server with hot reloading:

```
npm run dev
```

## Testing

Currently, there are no automated tests configured for the frontend. This would be a good area for future improvement.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.
