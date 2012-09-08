from envy.url import URL
from controllers.stream import Graph
from controllers.static import Static
from controllers.admin import Admin

urls = (
    URL(r'^graph/?$', Graph.index),
    URL(r'^rpc/?$', Graph.control),
    URL(r'^display/?$', Graph.display),
    URL(r'^static/(?P<file>[-\w.]+)/?$', Static.index),
    URL(r'^admin/?$', Admin.index),
    URL(r'^admin/save/?$', Admin.save),
    URL(r'^favico.ico/?$', Static.index),
)