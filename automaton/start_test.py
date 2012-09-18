from node.manager import Manager
from node.test import Test
from node.aquaponics import Aquaponics
import settings


aq = Manager(nodes=[[Test, 'Aquaponics'],], publisher=settings.PUBLISHER_PORT, rpc=settings.RPC_PORT)