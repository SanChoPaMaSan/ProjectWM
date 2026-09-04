import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


SYSTEM_PREFIX = '[WM] '


def event_graph(bp):
    return next((item for item in BlueprintTools.list_graphs(bp)
                 if item.get_name() == 'EventGraph'), None)


def clear_system_comments(editor):
    for comment in list(editor.list_comment_nodes()):
        if comment.get_comment_text().startswith(SYSTEM_PREFIX):
            editor.remove_comment_node(comment)


def add_group_comment(editor, text, nodes, color):
    if not nodes:
        return False
    comment = editor.add_comment_to_nodes(SYSTEM_PREFIX + text, nodes, 60)
    comment.set_comment_color(unreal.LinearColor(*color, 1.0))
    return True


def find_nodes(graph, names=(), titles=()):
    result = []
    for node in BlueprintTools.find_nodes(graph):
        if node.get_name() in names or node.get_node_title() in titles:
            result.append(node)
    return result


def organize_vehicle():
    path = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'
    bp = unreal.load_asset(path)
    if not bp:
        raise RuntimeError('Missing {}'.format(path))
    graph = event_graph(bp)
    if not graph:
        raise RuntimeError('Missing EventGraph in {}'.format(path))

    editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
    clear_system_comments(editor)

    # 화면 배치만 바꾼다. 핀 연결, 기본값, 로직은 건드리지 않는다.
    comment_nodes = set(editor.list_comment_nodes())
    logic_nodes = [node for node in BlueprintTools.find_nodes(graph)
                   if node not in comment_nodes]
    BlueprintTools.arrange_nodes(logic_nodes)

    groups = (
        ('입력 및 쓰레기 선택  |  좌클릭: 조준 시작·발사',
         find_nodes(graph, names=('K2Node_InputKey_2', 'K2Node_VariableGet_50'),
                    titles=('BeginTrashAim', 'ReleaseTrashAimAndEject')),
         (0.12, 0.35, 0.80)),
        ('흡수 입력  |  우클릭 홀드, 흡수 게이지 0이면 잠금',
         find_nodes(graph, names=('K2Node_InputKey_1',), titles=('Set IsSuctioning',)),
         (0.05, 0.60, 0.55)),
        ('서버 흡수 및 인벤토리  |  서버가 쓰레기 보관·동기화',
         find_nodes(graph, titles=('Server_SuctionTrash', 'SuctionTrash')),
         (0.28, 0.62, 0.25)),
        ('발사 조준  |  예측 경로 점선을 실시간 표시',
         find_nodes(graph, titles=('BeginTrashAim',)),
         (0.85, 0.55, 0.08)),
        ('서버 발사  |  선택한 쓰레기를 서버 권한으로 방출',
         find_nodes(graph, titles=('ReleaseTrashAimAndEject', 'ServerEjectSelectedTrash', 'Server_EjectTrash')),
         (0.75, 0.25, 0.18)),
    )
    added = sum(1 for text, nodes, color in groups if add_group_comment(editor, text, nodes, color))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    if not unreal.EditorAssetLibrary.save_loaded_asset(bp):
        raise RuntimeError('Could not save {}'.format(path))
    return added


def organize_trash(path, text, color):
    bp = unreal.load_asset(path)
    if not bp:
        raise RuntimeError('Missing {}'.format(path))
    graph = event_graph(bp)
    if not graph:
        raise RuntimeError('Missing EventGraph in {}'.format(path))
    editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
    clear_system_comments(editor)
    comment = editor.add_comment_node(SYSTEM_PREFIX + text, unreal.Vector2D(-400.0, -260.0), unreal.Vector2D(900.0, 180.0))
    comment.set_comment_color(unreal.LinearColor(*color, 1.0))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    if not unreal.EditorAssetLibrary.save_loaded_asset(bp):
        raise RuntimeError('Could not save {}'.format(path))


vehicle_count = organize_vehicle()
organize_trash('/Game/Fab/Trash/T/BP_Trash1',
               '쓰레기 1 - 넉백  |  충돌한 플레이어를 밀어냄 (C++ TrashKnockbackActor)',
               (0.70, 0.18, 0.18))
organize_trash('/Game/Fab/Trash/T/BP_Trash2',
               '쓰레기 2 - 감속 장판  |  방출 후 튕기는 충돌 지점마다 3초 장판, 이동속도 30% 감소 (C++ TrashSlowZoneActor)',
               (0.42, 0.18, 0.72))
organize_trash('/Game/Fab/Trash/T/BP_Trash3',
               '쓰레기 3 - 박스 표창  |  낮고 멀리 발사되며 공중에서 회전 (C++ StunDeliveryVehicle)',
               (0.85, 0.52, 0.08))
organize_trash('/Game/Fab/Trash/T/BP_Trash4',
               '쓰레기 4 - 똥 스턴  |  적중 시 5초 스턴 (C++ StunTrashActor)',
               (0.82, 0.30, 0.10))
unreal.log_warning('WM_BLUEPRINT_COMMENTS saved vehicle_groups={}'.format(vehicle_count))
