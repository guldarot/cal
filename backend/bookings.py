from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Event, TimeSlot, Booking
from backend.utils import fan_required
from backend.notifications import send_booking_confirmation_fan, send_booking_notification_admin
from backend.security import validate_and_sanitize_json, rate_limit
from sqlalchemy.exc import IntegrityError

bp = Blueprint('bookings', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
@fan_required
@validate_and_sanitize_json()
@rate_limit(max_requests=30, window=3600)  # 30 requests per hour
def create_booking():
    """Create a new booking (fan only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['time_slot_id', 'fan_name', 'fan_email', 'fan_phone']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        time_slot_id = data['time_slot_id']
        fan_name = data['fan_name'].strip()
        fan_email = data['fan_email'].strip().lower()
        fan_phone = data['fan_phone'].strip()
        
        # Validate email format
        from backend.utils import validate_email
        if not validate_email(fan_email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate phone format (simple validation)
        if len(fan_phone) < 10 or len(fan_phone) > 15:
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Find the time slot
        time_slot = TimeSlot.query.filter_by(id=time_slot_id).first()
        if not time_slot:
            return jsonify({'error': 'Time slot not found'}), 404
        
        # Check if the time slot is already booked
        if time_slot.is_booked:
            return jsonify({'error': 'Time slot already booked'}), 409
        
        # Get the event for this time slot
        event = time_slot.event
        if not event.is_published:
            return jsonify({'error': 'Cannot book unpublished event'}), 400
        
        # Create booking
        booking = Booking(
            time_slot_id=time_slot_id,
            fan_id=current_user_id,
            fan_name=fan_name,
            fan_email=fan_email,
            fan_phone=fan_phone
        )
        
        # Add booking to database
        db.session.add(booking)
        
        # Mark time slot as booked
        time_slot.is_booked = True
        
        # Commit all changes
        db.session.commit()
        
        # Send booking confirmation emails
        send_booking_confirmation_fan(booking, event, time_slot, current_app)
        send_booking_notification_admin(booking, event, time_slot, event.admin, current_app)
        
        # Prepare response
        booking_dict = booking.to_dict()
        booking_dict['event'] = {
            'id': event.id,
            'title': event.title,
            'event_date': event.event_date.isoformat() if event.event_date else None
        }
        booking_dict['time_slot'] = {
            'start_time': time_slot.start_time.isoformat() if time_slot.start_time else None,
            'end_time': time_slot.end_time.isoformat() if time_slot.end_time else None
        }
        
        return jsonify(booking_dict), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Time slot already booked'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create booking', 'details': str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
@fan_required
@rate_limit(max_requests=60, window=3600)  # 60 requests per hour
def get_user_bookings():
    """Get all bookings made by the authenticated fan"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query bookings for this fan
        bookings_query = Booking.query.filter_by(fan_id=current_user_id)\
            .join(TimeSlot)\
            .join(Event)\
            .order_by(Booking.created_at.desc())
        
        bookings_pagination = bookings_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Prepare response data
        bookings_data = []
        for booking in bookings_pagination.items:
            booking_dict = booking.to_dict()
            booking_dict['event'] = booking.time_slot.event.to_public_dict()
            booking_dict['time_slot'] = booking.time_slot.to_public_dict()
            bookings_data.append(booking_dict)
        
        return jsonify({
            'bookings': bookings_data,
            'pagination': {
                'page': bookings_pagination.page,
                'per_page': bookings_pagination.per_page,
                'total': bookings_pagination.total,
                'pages': bookings_pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve bookings', 'details': str(e)}), 500

@bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
@rate_limit(max_requests=120, window=3600)  # 120 requests per hour
def get_booking(booking_id):
    """Get detailed information about a specific booking"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Find booking
        booking = Booking.query.filter_by(id=booking_id).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check if user has permission to view this booking
        if user.is_fan() and booking.fan_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if user.is_admin() and booking.time_slot.event.admin_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Prepare response
        booking_dict = booking.to_dict()
        booking_dict['event'] = booking.time_slot.event.to_dict()
        booking_dict['time_slot'] = booking.time_slot.to_dict()
        
        return jsonify(booking_dict), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve booking', 'details': str(e)}), 500

@bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
@fan_required
@rate_limit(max_requests=10, window=3600)  # 10 requests per hour
def cancel_booking(booking_id):
    """Cancel a booking (fan only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find booking
        booking = Booking.query.filter_by(id=booking_id, fan_id=current_user_id).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found or access denied'}), 404
        
        # Get the time slot and event
        time_slot = booking.time_slot
        event = time_slot.event
        
        # Mark time slot as available
        time_slot.is_booked = False
        
        # Delete booking
        db.session.delete(booking)
        db.session.commit()
        
        # In a real application, you would send a cancellation email here
        # For now, we'll just return a success message
        
        return jsonify({'message': 'Booking cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel booking', 'details': str(e)}), 500