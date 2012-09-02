from envy.url import URL
from controllers.stream import Graph

urls = (
    URL(r'^graph/humidity/?$', Graph.humidity),
    URL(r'^graph/ph/?$', Graph.ph),
    URL(r'^graph/display/?$', Graph.display),
)