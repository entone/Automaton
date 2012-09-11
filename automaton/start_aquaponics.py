from node.manager import Manager
from node.test import Test
from node.aquaponics import Aquaponics


aq = Manager(nodes=[[Aquaponics, 'Lettuce'], [Test, 'Basil']], publisher=5554, rpc=5553)