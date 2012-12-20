from envy.url import URL
from controllers.realtime import Realtime
from controllers.dashboard import Dashboard
from controllers.api import API
from controllers.user import User
from controllers.historical import Historical
from controllers.static import Static

urls = (
    URL(r'^graph/?$', Realtime.index),
    URL(r'^graph/historical/(?P<name>[-\w.]+)/?$', Realtime.historical),
    URL(r'^rpc/?$', Realtime.control),
    URL(r'^realtime/(?P<id>[-\w.]+)?$', Realtime.display),
    URL(r'^dashboard/?$', Dashboard.index),
    URL(r'^historical/?$', Historical.index),
    URL(r'^historical/csv/(?P<node_id>[-\w.]+)/(?P<type>[-\w.]+)/(?P<frm>[-\w.]+)/(?P<to>[-\w.]+)/?$', Historical.csv),
    URL(r'^historical/csv/(?P<node_id>[-\w.]+)/(?P<type>[-\w.]+)/?$', Historical.csv),
    URL(r'^historical/data/(?P<node_id>[-\w.]+)/(?P<type>[-\w.]+)/(?P<frm>[-\w.]+)/(?P<to>[-\w.]+)/?$', Historical.data),
    URL(r'^historical/data/(?P<node_id>[-\w.]+)/(?P<type>[-\w.]+)/?$', Historical.data),
    URL(r'^api/register_location/?$', API.register_location),
    URL(r'^api/add_node/?$', API.add_node),
    URL(r'^api/sensor_values/?$', API.sensor_values),
    URL(r'^signup/?$', User.signup),
    URL(r'^signin/?$', User.signin),
    URL(r'^signout/?$', User.signout),
    URL(r'^auth/?$', User.auth),
    URL(r'^create_account/?$', User.create_account),
    URL(r'^static/(?P<file>[-\w.]+)/?$', Static.index),
    URL(r'^favico.ico/?$', Static.index),

)