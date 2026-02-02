from .user import (
    create_user,
    create_driver,
    create_customer,
    create_owner,
    get_user_by_username,
    get_user,
    get_all_users,
    get_all_users_json,
    update_user
)
from .auth import login, setup_jwt, add_auth_context
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()

    driver = create_driver(
        name ='John_Driver',
        email ='driver@test.com',
        password ='password',
        address ='123 Main Street, Port of Spain'
        #role='driver'
    )

    print(f'Created driver: {driver.name} with Email: {driver.email}')

    owner = create_owner(
        name='Alice_Owner', 
        email = 'owner@test.com',
        password = 'password',
        address = '456 Oak Avenue, Port of Spain'
        #role='owner'
    )

    print(f'Created owner: {owner.name} with Email: {owner.email}')

    customer = create_customer(
        name ='Bob_Customer',
        email ='customer@test.com',
        password ='password',
        address ='789 Pine Road, Port of Spain'
        #role='customer'
    )

    print(f'Created customer: {customer.name} with Email: {customer.email}')