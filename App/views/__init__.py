from .user   import user_views
from .driver import driver_views
from .customer import customer_views
from .index  import index_views
from .auth   import auth_views
from .admin  import setup_admin

views = [user_views, index_views, auth_views, customer_views, driver_views]
