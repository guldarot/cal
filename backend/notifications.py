from flask import render_template_string
from flask_mail import Message
from backend.app import mail
from threading import Thread
import os

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

def send_email(to, subject, template, app, **kwargs):
    """Send an email using Flask-Mail"""
    # Render HTML and text versions of the email
    html_body = render_template_string(template, **kwargs)
    
    # Create a simple text version by removing HTML tags
    text_body = html_body.replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n')
    text_body = ''.join([s for s in text_body if not (s.startswith('<') and s.endswith('>'))])
    
    # Create the email message
    msg = Message(
        subject=subject,
        recipients=[to],
        html=html_body,
        body=text_body
    )
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(app, msg)).start()

# Email templates
registration_confirmation_template = """
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
"""

booking_confirmation_fan_template = """
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
"""

booking_notification_admin_template = """
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
"""

booking_cancellation_template = """
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
"""

password_reset_template = """
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
"""

def send_registration_confirmation(user, app):
    """Send registration confirmation email"""
    verification_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:5173')}/verify-email?token=sample_token"
    
    send_email(
        to=user.email,
        subject="Welcome to Appointment Booking System",
        template=registration_confirmation_template,
        app=app,
        user=user,
        verification_url=verification_url
    )

def send_booking_confirmation_fan(booking, event, time_slot, app):
    """Send booking confirmation email to fan"""
    send_email(
        to=booking.fan_email,
        subject="Booking Confirmation",
        template=booking_confirmation_fan_template,
        app=app,
        fan_name=booking.fan_name,
        event_title=event.title,
        event_date=event.event_date,
        start_time=time_slot.start_time,
        end_time=time_slot.end_time
    )

def send_booking_notification_admin(booking, event, time_slot, admin, app):
    """Send booking notification email to admin"""
    send_email(
        to=admin.email,
        subject="New Booking for Your Event",
        template=booking_notification_admin_template,
        app=app,
        admin_name=admin.name,
        fan_name=booking.fan_name,
        fan_email=booking.fan_email,
        fan_phone=booking.fan_phone,
        event_title=event.title,
        event_date=event.event_date,
        start_time=time_slot.start_time,
        end_time=time_slot.end_time
    )

def send_booking_cancellation(user_name, user_email, event, time_slot, app):
    """Send booking cancellation email"""
    send_email(
        to=user_email,
        subject="Booking Cancellation",
        template=booking_cancellation_template,
        app=app,
        user_name=user_name,
        event_title=event.title,
        event_date=event.event_date,
        start_time=time_slot.start_time,
        end_time=time_slot.end_time
    )

def send_password_reset(user, reset_url, app):
    """Send password reset email"""
    send_email(
        to=user.email,
        subject="Password Reset",
        template=password_reset_template,
        app=app,
        user_name=user.name,
        reset_url=reset_url
    )