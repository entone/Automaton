from envy.url import URL
from controllers.stream import Graph
from controllers.static import Static

urls = (
    URL(r'^graph/?$', Graph.index),
    URL(r'^rpc/?$', Graph.control),
    URL(r'^display/?$', Graph.display),
    URL(r'^static/(?P<file>[-\w.]+)/?$', Static.index),
)