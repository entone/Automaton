from envy.url import URL
from controllers.stream import Graph

urls = (
    URL(r'^graph/?$', Graph.index),
    URL(r'^rpc/?$', Graph.control),
    URL(r'^graph/display/?$', Graph.display),
)