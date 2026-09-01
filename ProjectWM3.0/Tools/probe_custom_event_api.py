import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')
import unreal

names = [name for name in dir(unreal.K2Node_CustomEvent) if 'pin' in name.lower() or 'function' in name.lower() or 'flag' in name.lower() or 'rpc' in name.lower()]
unreal.log_warning('CUSTOM_EVENT_API {}'.format(names))
