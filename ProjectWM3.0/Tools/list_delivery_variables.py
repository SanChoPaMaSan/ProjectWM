import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

bp = unreal.load_asset('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1')
for name in BlueprintTools.list_variables(bp):
    try:
        replication = BlueprintTools.get_variable_replication(bp, name)
    except Exception:
        replication = 'ERR'
    unreal.log_warning('DELIVERY_VAR {} {}'.format(name, replication))
