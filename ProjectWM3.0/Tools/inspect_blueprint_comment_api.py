import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


bp = unreal.load_asset('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1')
graph = next(item for item in BlueprintTools.list_graphs(bp) if item.get_name() == 'EventGraph')
editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
unreal.log_warning('COMMENT_API editor_methods={}'.format(
    ','.join(name for name in dir(editor) if 'comment' in name.lower())))
unreal.log_warning('COMMENT_API comment_class={}'.format(
    unreal.load_class(None, '/Script/BlueprintGraph.EdGraphNode_Comment')))
unreal.log_warning('COMMENT_API graph_methods={}'.format(
    ','.join(name for name in dir(graph) if 'node' in name.lower() or 'comment' in name.lower())))
for name in ('add_comment_node', 'add_comment_to_nodes', 'list_comment_nodes', 'remove_comment_node'):
    method = getattr(editor, name)
    unreal.log_warning('COMMENT_API {}={}'.format(name, getattr(method, '__doc__', str(method))))
comments = list(editor.list_comment_nodes())
unreal.log_warning('COMMENT_API existing_count={}'.format(len(comments)))
if comments:
    comment = comments[0]
    unreal.log_warning('COMMENT_API comment_methods={}'.format(
        ','.join(name for name in dir(comment) if 'comment' in name.lower() or 'node' in name.lower() or 'color' in name.lower())))
for comment in comments:
    unreal.log_warning('COMMENT_API existing text={} pos={} size={}'.format(
        comment.get_comment_text(), comment.get_node_pos(), comment.get_node_size()))
for node in BlueprintTools.find_nodes(graph):
    unreal.log_warning('COMMENT_NODE {} | {} | {}'.format(
        node.get_name(), node.get_node_title(), node.get_node_pos()))
