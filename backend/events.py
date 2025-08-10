from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Event, TimeSlot, Booking
from backend.utils import admin_required
from backend.security import validate_and_sanitize_json, rate_limit
from datetime import datetime, date
import re

bp = Blueprint('events', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
@validate_and_sanitize_json()
@rate_limit(max_requests=30, window=3600)  # 30 requests per hour
def create_event():
    """Create a new event (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'event_date', 'time_slots']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        title = data['title'].strip()
        description = data['description'].strip() if 'description' in data and data['description'] else ''
        
        # Validate and parse event date
        try:
            event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate time slots
        time_slots_data = data['time_slots']
        if not isinstance(time_slots_data, list) or len(time_slots_data) == 0:
            return jsonify({'error': 'At least one time slot is required'}), 400
        
        # Create event
        event = Event(
            admin_id=current_user_id,
            title=title,
            description=description,
            event_date=event_date
        )
        
        # Add event to database to get ID
        db.session.add(event)
        db.session.flush()
        
        # Create time slots
        time_slots = []
        for slot_data in time_slots_data:
            if 'start_time' not in slot_data or 'end_time' not in slot_data:
                db.session.rollback()
                return jsonify({'error': 'Each time slot must have start_time and end_time'}), 400
            
            try:
                start_time = datetime.strptime(slot_data['start_time'], '%H:%M').time()
                end_time = datetime.strptime(slot_data['end_time'], '%H:%M').time()
            except ValueError:
                db.session.rollback()
                return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
            
            # Validate that start_time is before end_time
            if start_time >= end_time:
                db.session.rollback()
                return jsonify({'error': 'Start time must be before end time'}), 400
            
            time_slot = TimeSlot(
                event_id=event.id,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(time_slot)
            time_slots.append(time_slot)
        
        # Commit all changes
        db.session.commit()
        
        # Prepare response
        event_dict = event.to_dict()
        event_dict['time_slots'] = [slot.to_dict() for slot in time_slots]
        
        return jsonify(event_dict), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create event', 'details': str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
@rate_limit(max_requests=60, window=3600)  # 60 requests per hour
def get_admin_events():
    """Get all events created by the authenticated admin"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query events for this admin
        events_query = Event.query.filter_by(admin_id=current_user_id)
        events_pagination = events_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Prepare response data
        events_data = []
        for event in events_pagination.items:
            # Count bookings for this event
            bookings_count = TimeSlot.query.join(Booking).filter(
                TimeSlot.event_id == event.id
            ).count()
            
            event_dict = event.to_dict()
            event_dict['bookings_count'] = bookings_count
            events_data.append(event_dict)
        
        return jsonify({
            'events': events_data,
            'pagination': {
                'page': events_pagination.page,
                'per_page': events_pagination.per_page,
                'total': events_pagination.total,
                'pages': events_pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve events', 'details': str(e)}), 500

@bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
@admin_required
@rate_limit(max_requests=120, window=3600)  # 120 requests per hour
def get_event(event_id):
    """Get detailed information about a specific event"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find event and ensure it belongs to the current admin
        event = Event.query.filter_by(id=event_id, admin_id=current_user_id).first()
        
        if not event:
            return jsonify({'error': 'Event not found or access denied'}), 404
        
        # Get time slots for this event
        time_slots = TimeSlot.query.filter_by(event_id=event_id).all()
        
        # Prepare response
        event_dict = event.to_dict()
        event_dict['time_slots'] = [slot.to_dict() for slot in time_slots]
        
        return jsonify(event_dict), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve event', 'details': str(e)}), 500

@bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
@admin_required
@validate_and_sanitize_json()
@rate_limit(max_requests=30, window=3600)  # 30 requests per hour
def update_event(event_id):
    """Update an existing event"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find event and ensure it belongs to the current admin
        event = Event.query.filter_by(id=event_id, admin_id=current_user_id).first()
        
        if not event:
            return jsonify({'error': 'Event not found or access denied'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update title if provided
        if 'title' in data and data['title']:
            event.title = data['title'].strip()
        
        # Update description if provided
        if 'description' in data:
            event.description = data['description'].strip()
        
        # Update event date if provided
        if 'event_date' in data and data['event_date']:
            try:
                event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
                event.event_date = event_date
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Update time slots if provided
        if 'time_slots' in data and isinstance(data['time_slots'], list):
            # Delete existing time slots
            TimeSlot.query.filter_by(event_id=event_id).delete()
            
            # Create new time slots
            for slot_data in data['time_slots']:
                if 'start_time' not in slot_data or 'end_time' not in slot_data:
                    db.session.rollback()
                    return jsonify({'error': 'Each time slot must have start_time and end_time'}), 400
                
                try:
                    start_time = datetime.strptime(slot_data['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(slot_data['end_time'], '%H:%M').time()
                except ValueError:
                    db.session.rollback()
                    return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
                
                # Validate that start_time is before end_time
                if start_time >= end_time:
                    db.session.rollback()
                    return jsonify({'error': 'Start time must be before end time'}), 400
                
                time_slot = TimeSlot(
                    event_id=event_id,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(time_slot)
        
        # Commit changes
        db.session.commit()
        
        # Get updated time slots
        time_slots = TimeSlot.query.filter_by(event_id=event_id).all()
        
        # Prepare response
        event_dict = event.to_dict()
        event_dict['time_slots'] = [slot.to_dict() for slot in time_slots]
        
        return jsonify({
            'message': 'Event updated successfully',
            'event': event_dict
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update event', 'details': str(e)}), 500

@bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@rate_limit(max_requests=10, window=3600)  # 10 requests per hour
def delete_event(event_id):
    """Delete an event and all associated time slots and bookings"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find event and ensure it belongs to the current admin
        event = Event.query.filter_by(id=event_id, admin_id=current_user_id).first()
        
        if not event:
            return jsonify({'error': 'Event not found or access denied'}), 404
        
        # Delete event (this will cascade to time slots and bookings)
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'message': 'Event deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete event', 'details': str(e)}), 500

@bp.route('/<int:event_id>/publish', methods=['POST'])
@jwt_required()
@admin_required
@validate_and_sanitize_json()
@rate_limit(max_requests=20, window=3600)  # 20 requests per hour
def publish_event(event_id):
    """Publish or unpublish an event"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find event and ensure it belongs to the current admin
        event = Event.query.filter_by(id=event_id, admin_id=current_user_id).first()
        
        if not event:
            return jsonify({'error': 'Event not found or access denied'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required field
        if 'is_published' not in data:
            return jsonify({'error': 'is_published is required'}), 400
        
        is_published = bool(data['is_published'])
        event.is_published = is_published
        
        db.session.commit()
        
        return jsonify({
            'id': event.id,
            'is_published': event.is_published,
            'message': 'Event published/unpublished successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update event status', 'details': str(e)}), 500

@bp.route('/<int:event_id>/bookings', methods=['GET'])
@jwt_required()
@admin_required
@rate_limit(max_requests=60, window=3600)  # 60 requests per hour
def get_event_bookings(event_id):
    """Get all bookings for a specific event"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find event and ensure it belongs to the current admin
        event = Event.query.filter_by(id=event_id, admin_id=current_user_id).first()
        
        if not event:
            return jsonify({'error': 'Event not found or access denied'}), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query bookings for this event
        bookings_query = Booking.query.join(TimeSlot).filter(
            TimeSlot.event_id == event_id
        ).order_by(Booking.created_at.desc())
        
        bookings_pagination = bookings_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Prepare response data
        bookings_data = []
        for booking in bookings_pagination.items:
            time_slot = booking.time_slot
            booking_event = time_slot.event
            booking_dict = booking.to_dict()
            booking_dict['event'] = {
                'id': booking_event.id,
                'title': booking_event.title,
                'event_date': booking_event.event_date.isoformat() if booking_event.event_date else None
            }
            booking_dict['time_slot'] = {
                'start_time': time_slot.start_time.isoformat() if time_slot.start_time else None,
                'end_time': time_slot.end_time.isoformat() if time_slot.end_time else None
            }
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


@bp.route('/bookings', methods=['GET'])
@jwt_required()
@admin_required
@rate_limit(max_requests=60, window=3600)  # 60 requests per hour
def get_admin_bookings():
    """Get all bookings for all events of the authenticated admin"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query bookings for all events of this admin
        bookings_query = Booking.query.join(TimeSlot).join(Event).filter(
            Event.admin_id == current_user_id
        ).order_by(Booking.created_at.desc())
        
        bookings_pagination = bookings_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Prepare response data
        bookings_data = []
        for booking in bookings_pagination.items:
            time_slot = booking.time_slot
            booking_event = time_slot.event
            booking_dict = booking.to_dict()
            booking_dict['event'] = {
                'id': booking_event.id,
                'title': booking_event.title,
                'event_date': booking_event.event_date.isoformat() if booking_event.event_date else None
            }
            booking_dict['time_slot'] = {
                'start_time': time_slot.start_time.isoformat() if time_slot.start_time else None,
                'end_time': time_slot.end_time.isoformat() if time_slot.end_time else None
            }
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

@bp.route('/public/<string:event_url>', methods=['GET'])
def get_public_event(event_url):
    """Get event details by unique URL"""
    try:
        # Find published event by unique URL
        event = Event.query.filter_by(unique_url=event_url, is_published=True).first()
        
        if not event:
            return jsonify({'error': 'Event not found or not published'}), 404
        
        return jsonify(event.to_public_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve event', 'details': str(e)}), 500

@bp.route('/public/<string:event_url>/slots', methods=['GET'])
def get_public_event_slots(event_url):
    """Get available time slots for an event"""
    try:
        # Find published event by unique URL
        event = Event.query.filter_by(unique_url=event_url, is_published=True).first()
        
        if not event:
            return jsonify({'error': 'Event not found or not published'}), 404
        
        # Get available time slots (not booked)
        time_slots = TimeSlot.query.filter_by(event_id=event.id, is_booked=False).all()
        
        # Prepare response data
        slots_data = [slot.to_public_dict() for slot in time_slots]
        
        return jsonify({'time_slots': slots_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve time slots', 'details': str(e)}), 500