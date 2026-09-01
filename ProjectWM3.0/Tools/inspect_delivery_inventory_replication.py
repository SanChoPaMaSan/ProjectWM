import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'
NAMES = ('HeldTrash1', 'HeldTrash2', 'HeldTrash3', 'HeldTrash4', 'TrashReleaseQueue', 'CurrentEjectActor', 'CurrentEjectMesh', 'CurrentTrash', 'CurrentTrashType')

bp = unreal.load_asset(PATH)
if not bp:
    raise RuntimeError('Missing blueprint')

for name in NAMES:
    try:
        replication = BlueprintTools.get_variable_replication(bp, name)
    except Exception as exc:
        replication = 'ERROR:{}'.format(exc)
    unreal.log_warning('INV_REP {}={}'.format(name, replication))
