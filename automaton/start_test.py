from node.manager import Manager
from node.test import Test

aq = Manager(nodes=[Test], publisher=5554, rpc=5553)