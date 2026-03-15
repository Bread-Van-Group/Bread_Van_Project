from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
import uuid

# Create blueprint
driver_views = Blueprint('driver_views', __name__, template_folder='../templates')

# In-memory storage for items (in production, use a database)
driver_transactions = {}

@driver_views.route('/driver/home', methods=['GET'])
@jwt_required()
def driver_homepage():
    """Render the main driver transaction page"""
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    # Generate or retrieve session ID for this driver
    driver_id = get_jwt_identity()
    session_id = session.get(f'driver_session_{driver_id}')
    
    if not session_id:
        session_id = str(uuid.uuid4())
        session[f'driver_session_{driver_id}'] = session_id
        driver_transactions[session_id] = {'items': [], 'total': 0, 'driver_id': driver_id}
    
    return render_template('driver/transaction.html')

@driver_views.route('/driver/api/items', methods=['GET'])
@jwt_required()
def get_items():
    """Get all items for the current driver session"""
    if current_user.role != 'driver':
        return jsonify({'error': 'Unauthorized'}), 403
    
    driver_id = get_jwt_identity()
    session_id = session.get(f'driver_session_{driver_id}')
    
    if not session_id or session_id not in driver_transactions:
        return jsonify({'items': [], 'total': 0})
    
    # Return current items and total
    return jsonify({
        'items': driver_transactions.get(session_id, {}).get('items', []),
        'total': driver_transactions.get(session_id, {}).get('total', 0)
    })

@driver_views.route('/driver/api/items/add', methods=['POST'])
@jwt_required()
def add_item():
    """Add a new item to the driver's transaction"""
    if current_user.role != 'driver':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        driver_id = get_jwt_identity()
        session_id = session.get(f'driver_session_{driver_id}')
        
        if not session_id:
            session_id = str(uuid.uuid4())
            session[f'driver_session_{driver_id}'] = session_id
            driver_transactions[session_id] = {'items': [], 'total': 0, 'driver_id': driver_id}
        
        data = request.get_json()
        
        # Create new item with unique ID
        new_item = {
            'id': str(uuid.uuid4()),
            'name': data.get('name', ''),
            'quantity': int(data.get('quantity', 1)),
            'price': float(data.get('price', 0))
        }
        
        # Add item to transaction
        driver_transactions[session_id]['items'].append(new_item)
        
        # Recalculate total
        driver_transactions[session_id]['total'] = sum(
            item['quantity'] * item['price'] 
            for item in driver_transactions[session_id]['items']
        )
        
        return jsonify({
            'success': True,
            'items': driver_transactions[session_id]['items'],
            'total': driver_transactions[session_id]['total']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@driver_views.route('/driver/api/items/clear', methods=['POST'])
@jwt_required()
def clear_items():
    """Clear all items from the driver's transaction"""
    if current_user.role != 'driver':
        return jsonify({'error': 'Unauthorized'}), 403
    
    driver_id = get_jwt_identity()
    session_id = session.get(f'driver_session_{driver_id}')
    
    if session_id and session_id in driver_transactions:
        driver_transactions[session_id] = {'items': [], 'total': 0, 'driver_id': driver_id}
        
        return jsonify({
            'success': True,
            'items': [],
            'total': 0
        })
    
    return jsonify({'success': False, 'error': 'Session not found'}), 404

@driver_views.route('/driver/api/transactions/complete', methods=['POST'])
@jwt_required()
def complete_transaction():
    """Complete the current transaction"""
    if current_user.role != 'driver':
        return jsonify({'error': 'Unauthorized'}), 403
    
    driver_id = get_jwt_identity()
    session_id = session.get(f'driver_session_{driver_id}')
    
    if session_id and session_id in driver_transactions:
        # Here you would typically save to database
        # For now, we'll just clear the session
        
        # In production, you might want to:
        # 1. Save transaction to database
        # 2. Generate receipt
        # 3. Send to backend systems
        # 4. Clear the current transaction
        
        transaction = driver_transactions[session_id]
        
        # Clear the transaction
        driver_transactions[session_id] = {'items': [], 'total': 0, 'driver_id': driver_id}
        
        return jsonify({
            'success': True,
            'message': 'Transaction completed successfully',
            'transaction': transaction
        })
    
    return jsonify({'success': False, 'error': 'No active transaction'}), 404

@driver_views.route('/driver/transactions/history', methods=['GET'])
@jwt_required()
def transaction_history():
    """View driver's transaction history"""
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    # Here you would typically fetch from database
    # For now, we'll just render a template
    return render_template('driver/history.html')

@driver_views.route('/driver/deliveries', methods=['GET'])
@jwt_required()
def active_deliveries():
    """View driver's active deliveries"""
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    # Here you would typically fetch from database
    return render_template('driver/deliveries.html')

@driver_views.route('/driver/profile', methods=['GET'])
@jwt_required()
def driver_profile():
    """View driver's profile"""
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    return render_template('driver/profile.html')