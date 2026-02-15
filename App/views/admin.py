from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from flask_admin import Admin
from flask import flash, redirect, url_for, request
from App.database import db
from App.models import User, Driver, Customer, Owner, Van, Route, InventoryItem


class AdminView(ModelView):

    @jwt_required()
    def is_accessible(self):
        return current_user is not None and current_user.role == 'owner'

    def inaccessible_callback(self, name, **kwargs):
        flash("Login as an owner to access admin")
        return redirect(url_for('index_views.index', next=request.url))


def setup_admin(app):
    admin = Admin(app, name='BreadVan Admin', template_mode='bootstrap3')
    admin.add_view(AdminView(User,          db.session))
    admin.add_view(AdminView(Driver,        db.session))
    admin.add_view(AdminView(Customer,      db.session))
    admin.add_view(AdminView(Owner,         db.session))
    admin.add_view(AdminView(Van,           db.session))
    admin.add_view(AdminView(Route,         db.session))
    admin.add_view(AdminView(InventoryItem, db.session))
