from envy.url import URL
from controllers.node import Node
from controllers.static import Static

urls = (
    URL(r'^graph/?$', Node.index),
    URL(r'^graph/historical/(?P<name>[-\w.]+)/?$', Node.historical),
    URL(r'^rpc/?$', Node.control),
    URL(r'^display/?$', Node.display),
    URL(r'^static/(?P<file>[-\w.]+)/?$', Static.index),
    URL(r'^favico.ico/?$', Static.index),
)