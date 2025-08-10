# Notification System Design

## Overview
This document outlines the notification system for the appointment booking application. The system will send email notifications for key events and optionally SMS notifications for critical alerts.

## Notification Types

### 1. User Registration
- **Trigger**: When a new user registers
- **Recipients**: The newly registered user
- **Content**: Welcome message with account verification link

### 2. Event Booking Confirmation
- **Trigger**: When a fan successfully books a time slot
- **Recipients**: The fan who made the booking
- **Content**: Booking confirmation with event details and time slot information

### 3. Admin Booking Notification
- **Trigger**: When a fan books a time slot for an admin's event
- **Recipients**: The admin who created the event
- **Content**: Notification of new booking with fan details and booking information

### 4. Booking Cancellation
- **Trigger**: When a fan cancels a booking
- **Recipients**: The fan who cancelled and the event admin
- **Content**: Confirmation of cancellation

### 5. Password Reset
- **Trigger**: When a user requests a password reset
- **Recipients**: The user who requested the reset
- **Content**: Password reset link with expiration time

## Email System

### Technology
- **Library**: Flask-Mail for email sending
- **SMTP Provider**: Configurable (Gmail, SendGrid, AWS SES, etc.)
- **Templating**: Jinja2 templates for email content

### Email Templates

#### Registration Confirmation
```html
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Appointment Booking System</title>
</head>
<body>
    <h1>Welcome {{ user.name }}!</h1>
    <p>Thank you for registering with our Appointment Booking System.</p>
    <p>Please verify your email address by clicking the link below:</p>
    <p><a href="{{ verification_url }}">Verify Email Address</a></p>
    <p>If you didn't create an account, you can safely ignore this email.</p>
    <p>Best regards,<br>The Appointment Booking Team</p>
</body>
</html>
```

#### Booking Confirmation (Fan)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Booking Confirmation</title>
</head>
<body>
    <h1>Booking Confirmation</h1>
    <p>Hello {{ fan_name }},</p>
    <p>Your booking has been confirmed for the following event:</p>
    <ul>
        <li><strong>Event:</strong> {{ event_title }}</li>
        <li><strong>Date:</strong> {{ event_date }}</li>
        <li><strong>Time:</strong> {{ start_time }} - {{ end_time }}</li>
    </ul>
    <p>Please arrive on time for your appointment.</p>
    <p>If you need to cancel or reschedule, you can do so from your booking history page.</p>
    <p>Best regards,<br>The Appointment Booking Team</p>
</body>
</html>
```

#### New Booking Notification (Admin)
```html
<!DOCTYPE html>
<html>
<head>
    <title>New Booking for Your Event</title>
</head>
<body>
    <h1>New Booking for Your Event</h1>
    <p>Hello {{ admin_name }},</p>
    <p>A new booking has been made for your event "{{ event_title }}":</p>
    <ul>
        <li><strong>Fan Name:</strong> {{ fan_name }}</li>
        <li><strong>Fan Email:</strong> {{ fan_email }}</li>
        <li><strong>Fan Phone:</strong> {{ fan_phone }}</li>
        <li><strong>Date:</strong> {{ event_date }}</li>
        <li><strong>Time:</strong> {{ start_time }} - {{ end_time }}</li>
    </ul>
    <p>You can view all bookings for this event in your admin dashboard.</p>
    <p>Best regards,<br>The Appointment Booking Team</p>
</body>
</html>
```

#### Booking Cancellation
```html
<!DOCTYPE html>
<html>
<head>
    <title>Booking Cancellation</title>
</head>
<body>
    <h1>Booking Cancellation</h1>
    <p>Hello {{ user_name }},</p>
    <p>The following booking has been cancelled:</p>
    <ul>
        <li><strong>Event:</strong> {{ event_title }}</li>
        <li><strong>Date:</strong> {{ event_date }}</li>
        <li><strong>Time:</strong> {{ start_time }} - {{ end_time }}</li>
    </ul>
    <p>The time slot is now available for others to book.</p>
    <p>Best regards,<br>The Appointment Booking Team</p>
</body>
</html>
```

#### Password Reset
```html
<!DOCTYPE html>
<html>
<head>
    <title>Password Reset</title>
</head>
<body>
    <h1>Password Reset</h1>
    <p>Hello {{ user_name }},</p>
    <p>You have requested to reset your password. Click the link below to set a new password:</p>
    <p><a href="{{ reset_url }}">Reset Password</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request a password reset, you can safely ignore this email.</p>
    <p>Best regards,<br>The Appointment Booking Team</p>
</body>
</html>
```

### Email Configuration

#### Environment Variables
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

#### Flask-Mail Configuration
```python
from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT') or 587)
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)
```

## SMS System (Optional)

### Technology
- **Service**: Twilio API (primary choice)
- **Library**: twilio-python library
- **Fallback**: Other providers (AWS SNS, Nexmo)

### SMS Templates

#### Booking Confirmation (Fan)
```
Appointment Booking Confirmation
Hello {{ fan_name }},
Your booking for {{ event_title }} on {{ event_date }} at {{ start_time }} is confirmed.
View details: {{ booking_url }}
```

#### New Booking Notification (Admin)
```
New Booking Alert
Hello {{ admin_name }},
A new booking was made for "{{ event_title }}" on {{ event_date }} at {{ start_time }}.
Fan: {{ fan_name }}
View details: {{ admin_booking_url }}
```

### SMS Configuration

#### Environment Variables
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

#### Twilio Configuration
```python
from twilio.rest import Client

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')

client = Client(account_sid, auth_token)
```

## Notification Service Architecture

### Notification Service Class
```python
class NotificationService:
    def __init__(self, app):
        self.mail = Mail(app)
        self.sms_client = self._init_sms_client()
    
    def _init_sms_client(self):
        # Initialize SMS client if credentials are provided
        if os.environ.get('TWILIO_ACCOUNT_SID'):
            return Client(
                os.environ.get('TWILIO_ACCOUNT_SID'),
                os.environ.get('TWILIO_AUTH_TOKEN')
            )
        return None
    
    def send_email(self, to, subject, template, **kwargs):
        # Render email template
        html_body = render_template(f'emails/{template}.html', **kwargs)
        text_body = render_template(f'emails/{template}.txt', **kwargs)
        
        # Create and send email message
        msg = Message(
            subject=subject,
            recipients=[to],
            html=html_body,
            body=text_body
        )
        
        # Send email asynchronously
        Thread(target=self._send_async_email, args=(app, msg)).start()
    
    def send_sms(self, to, body):
        # Send SMS if SMS client is configured
        if self.sms_client and twilio_phone_number:
            try:
                message = self.sms_client.messages.create(
                    body=body,
                    from_=twilio_phone_number,
                    to=to
                )
                return message.sid
            except Exception as e:
                # Log error and fallback to email
                app.logger.error(f"SMS sending failed: {str(e)}")
                return None
        return None
    
    def _send_async_email(self, app, msg):
        # Send email asynchronously
        with app.app_context():
            try:
                self.mail.send(msg)
            except Exception as e:
                app.logger.error(f"Email sending failed: {str(e)}")
```

## Notification Triggers

### User Registration
```python
# In user registration endpoint
notification_service.send_email(
    to=user.email,
    subject="Welcome to Appointment Booking System",
    template="registration_confirmation",
    user=user,
    verification_url=verification_url
)
```

### Booking Creation
```python
# In booking creation endpoint
# Notify fan
notification_service.send_email(
    to=booking.fan_email,
    subject="Booking Confirmation",
    template="booking_confirmation_fan",
    fan_name=booking.fan_name,
    event_title=event.title,
    event_date=event.event_date,
    start_time=time_slot.start_time,
    end_time=time_slot.end_time
)

# Notify admin
notification_service.send_email(
    to=admin.email,
    subject="New Booking for Your Event",
    template="booking_notification_admin",
    admin_name=admin.name,
    fan_name=booking.fan_name,
    fan_email=booking.fan_email,
    fan_phone=booking.fan_phone,
    event_title=event.title,
    event_date=event.event_date,
    start_time=time_slot.start_time,
    end_time=time_slot.end_time
)

# Optional SMS to fan
notification_service.send_sms(
    to=booking.fan_phone,
    body=f"Your booking for {event.title} on {event.event_date} at {time_slot.start_time} is confirmed."
)
```

### Booking Cancellation
```python
# In booking cancellation endpoint
# Notify fan
notification_service.send_email(
    to=booking.fan_email,
    subject="Booking Cancellation",
    template="booking_cancellation",
    user_name=booking.fan_name,
    event_title=event.title,
    event_date=event.event_date,
    start_time=time_slot.start_time,
    end_time=time_slot.end_time
)

# Notify admin
notification_service.send_email(
    to=admin.email,
    subject="Booking Cancelled for Your Event",
    template="booking_cancellation_admin",
    admin_name=admin.name,
    fan_name=booking.fan_name,
    event_title=event.title,
    event_date=event.event_date,
    start_time=time_slot.start_time,
    end_time=time_slot.end_time
)
```

### Password Reset
```python
# In password reset request endpoint
notification_service.send_email(
    to=user.email,
    subject="Password Reset",
    template="password_reset",
    user_name=user.name,
    reset_url=reset_url
)
```

## Error Handling and Retry Logic

### Email Sending
- Implement retry logic with exponential backoff
- Log failed emails for manual retry
- Provide fallback mechanisms (e.g., if SMTP fails, try another provider)

### SMS Sending
- Handle Twilio API errors gracefully
- Log failed SMS messages
- Provide fallback to email notifications

### Monitoring
- Track notification delivery rates
- Monitor for failed notifications
- Set up alerts for notification service issues

## Security Considerations

### Email Security
- Use TLS/SSL for email transmission
- Store email credentials securely in environment variables
- Validate email addresses before sending

### SMS Security
- Store SMS credentials securely in environment variables
- Validate phone numbers before sending
- Implement rate limiting to prevent abuse

### Content Security
- Sanitize all user inputs in email/SMS templates
- Prevent email header injection
- Use parameterized templates to prevent injection attacks

## Performance Considerations

### Asynchronous Processing
- Send notifications asynchronously to avoid blocking API responses
- Use background tasks for bulk notifications
- Implement queue-based processing for high-volume scenarios

### Caching
- Cache email templates to reduce file I/O
- Cache frequently used notification content

### Scalability
- Design notification service to handle increased load
- Implement load balancing for notification services
- Use cloud-based email/SMS providers for scalability