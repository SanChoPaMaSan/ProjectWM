import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


expected = {
    '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1':
        ('입력 및 쓰레기 선택', '흡수 입력', '발사 조준', '서버 발사'),
    '/Game/Fab/Trash/T/BP_Trash1': ('쓰레기 1 - 넉백',),
    '/Game/Fab/Trash/T/BP_Trash2': ('쓰레기 2 - 감속 장판',),
    '/Game/Fab/Trash/T/BP_Trash3': ('쓰레기 3 - 박스 부메랑',),
    '/Game/Fab/Trash/T/BP_Trash4': ('쓰레기 4 - 똥 스턴',),
}

for path, required in expected.items():
    bp = unreal.load_asset(path)
    graph = next(item for item in BlueprintTools.list_graphs(bp) if item.get_name() == 'EventGraph')
    editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
    texts = [comment.get_comment_text() for comment in editor.list_comment_nodes()]
    missing = [item for item in required if not any(item in text for text in texts)]
    if missing:
        raise RuntimeError('{} missing {}'.format(path, missing))
    if path.endswith('BP_DeliveryVehicle_v1'):
        comment_nodes = set(editor.list_comment_nodes())
        logic_nodes = [node for node in BlueprintTools.find_nodes(graph)
                       if node not in comment_nodes]
        overlaps = 0
        for index, left in enumerate(logic_nodes):
            left_pos, left_size = left.get_node_pos(), left.get_node_size()
            for right in logic_nodes[index + 1:]:
                right_pos, right_size = right.get_node_pos(), right.get_node_size()
                intersects = (left_pos.x < right_pos.x + right_size.x and
                              left_pos.x + left_size.x > right_pos.x and
                              left_pos.y < right_pos.y + right_size.y and
                              left_pos.y + left_size.y > right_pos.y)
                overlaps += int(intersects)
        if overlaps:
            raise RuntimeError('{} has {} overlapping logic nodes'.format(path, overlaps))
    unreal.log_warning('WM_BLUEPRINT_COMMENT_VERIFY {} count={} ok'.format(path, len(texts)))
