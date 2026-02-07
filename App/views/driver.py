from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request
from App.controllers import create_user, initialize, get_all_pending_stop_requests, get_all_active_stop_requests, get_all_stop_requests

driver_views = Blueprint('driver_views', __name__, template_folder='../templates')

@driver_views.route('/api/driver/pending-requests', methods=['GET'])
@jwt_required()
def get_pending_stop_requests():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    pending_stop_requests = get_all_pending_stop_requests()

    return [req.to_dict() for req in pending_stop_requests]

@driver_views.route('/api/driver/active-requests', methods=['GET'])
@jwt_required()
def get_active_stop_requests():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    active_stop_requests = get_all_active_stop_requests()

    return [req.to_dict() for req in active_stop_requests]

@driver_views.route('/driver/home', methods=['GET'])
@jwt_required()
def driver_homepage():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))

    return render_template('driver/homepage.html')