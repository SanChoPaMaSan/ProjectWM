import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal

PATHS = [
    '/Game/Fab/Trash/T/BP_Trash1',
    '/Game/Fab/Trash/T/BP_Trash2',
    '/Game/Fab/Trash/T/BP_Trash3',
    '/Game/Fab/Trash/T/BP_Trash4',
]

for path in PATHS:
    bp = unreal.load_asset(path)
    generated = unreal.load_class(None, '{}.{}_C'.format(path, bp.get_name())) if bp else None
    cdo = unreal.get_default_object(generated) if generated else None
    if not cdo:
        unreal.log_error('TRASH_NET missing {}'.format(path))
        continue
    unreal.log_warning('TRASH_NET {} replicates={}'.format(bp.get_name(), cdo.replicates))
