import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import (
    initialize,
    get_all_users,
    get_all_users_json,
    create_customer,
    create_driver,
    create_owner,
)

app = create_app()
migrate = get_migrate(app)


# ── Init Command ──────────────────────────────────────────────────────────────

@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('Database initialized')


# ── User Commands ─────────────────────────────────────────────────────────────

user_cli = AppGroup('user', help='User object commands')


@user_cli.command("create-customer", help="Creates a customer user")
@click.argument("email")
@click.argument("password")
@click.argument("name")
@click.option("--address", default=None, help="Customer address")
@click.option("--phone",   default=None, help="Customer phone")
def create_customer_command(email, password, name, address, phone):
    user = create_customer(email=email, password=password, name=name,
                           address=address, phone=phone)
    if user:
        print(f'Customer {user.name} ({user.email}) created!')
    else:
        print(f'A user with email {email} already exists.')


@user_cli.command("create-driver", help="Creates a driver user")
@click.argument("email")
@click.argument("password")
@click.argument("name")
@click.option("--address", default=None, help="Driver address")
@click.option("--phone",   default=None, help="Driver phone")
def create_driver_command(email, password, name, address, phone):
    user = create_driver(email=email, password=password, name=name,
                         address=address, phone=phone)
    if user:
        print(f'Driver {user.name} ({user.email}) created!')
    else:
        print(f'A user with email {email} already exists.')


@user_cli.command("create-owner", help="Creates an owner user")
@click.argument("email")
@click.argument("password")
def create_owner_command(email, password):
    user = create_owner(email=email, password=password)
    if user:
        print(f'Owner ({user.email}) created!')
    else:
        print(f'A user with email {email} already exists.')


@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())


app.cli.add_command(user_cli)


# ── Test Commands ─────────────────────────────────────────────────────────────

test = AppGroup('test', help='Testing commands')


@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)