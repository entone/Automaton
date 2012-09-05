from interface.aquaponics import Aquaponics

aq = Aquaponics(publisher="tcp://*:5555", rpc="tcp://*:6666", node='lettuce')