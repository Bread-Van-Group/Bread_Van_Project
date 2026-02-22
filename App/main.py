import os
from flask import Flask, request, render_template, redirect, flash, url_for
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

from App.database import init_db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views, setup_admin

socketio = SocketIO(cors_allowed_origins="*")

#Websocket functions

@socketio.on("driver_location")
def handle_driver_location(data):
    print(data)
    socketio.emit("driver_update", data, skip_sid=request.sid)


def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    setup_admin(app)
    
    #Websockets code
    socketio.init_app(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        flash("Please log in first.", "error")
        return redirect(url_for('index_views.index'))

    @jwt.expired_token_loader
    def expired_callback(jwt_header, jwt_payload):
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for('index_views.index'))
    
    app.app_context().push()
    return app