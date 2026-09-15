import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


BASE = '/Game/Fab/Car/BP/'
CARS = (
    ('BP_Car1', '/Game/Fab/Car/SM_ClassicCar'),
    ('BP_Car2', '/Game/Fab/Car/SM_HatchbackCar'),
    ('BP_Car3', '/Game/Fab/Car/SM_MonsterTruck'),
    ('BP_Car4', '/Game/Fab/Car/SM_Van'),
    ('BP_Car5', '/Game/Fab/Car/SM_MuscleCar'),
    ('BP_Car6', '/Game/Fab/Car/SM_Pickup'),
    ('BP_Car7', '/Game/Fab/Car/SM_SportCar'),
)
SYSTEM_PREFIX = '[Traffic] '


def load_parent(path):
    parent = unreal.load_class(None, path)
    if not parent:
        raise RuntimeError('Missing parent {}'.format(path))
    return parent


def configure_comment(bp, text, color):
    graph = next(item for item in BlueprintTools.list_graphs(bp) if item.get_name() == 'EventGraph')
    editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
    for comment in list(editor.list_comment_nodes()):
        if comment.get_comment_text().startswith(SYSTEM_PREFIX):
            editor.remove_comment_node(comment)
    comment = editor.add_comment_node(SYSTEM_PREFIX + text, unreal.Vector2D(-420.0, -240.0), unreal.Vector2D(900.0, 170.0))
    comment.set_comment_color(unreal.LinearColor(*color, 1.0))


def reparent(path, parent):
    bp = unreal.load_asset(path)
    if not bp:
        raise RuntimeError('Missing {}'.format(path))
    if unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp) != parent:
        unreal.BlueprintEditorLibrary.reparent_blueprint(bp, parent)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    return bp


car_parent = load_parent('/Script/ProjectWM.TrafficCarActor')
start_parent = load_parent('/Script/ProjectWM.TrafficStartActor')
end_parent = load_parent('/Script/ProjectWM.TrafficEndActor')

car_classes = []
for bp_name, mesh_path in CARS:
    bp_path = BASE + bp_name
    bp = reparent(bp_path, car_parent)
    generated = unreal.load_class(None, bp_path + '.' + bp_name + '_C')
    cdo = unreal.get_default_object(generated) if generated else None
    components = cdo.get_components_by_class(unreal.StaticMeshComponent) if cdo else []
    component = components[0] if components else None
    mesh = unreal.load_asset(mesh_path)
    if not component or not isinstance(mesh, unreal.StaticMesh):
        raise RuntimeError('Could not configure {} mesh {}'.format(bp_name, mesh_path))
    component.set_editor_property('static_mesh', mesh)
    # Every imported car uses local -Y as its front. Keep visuals aligned with
    # TrafficCarActor's +X movement and with the StartBP arrow.
    component.set_editor_property('relative_rotation', unreal.Rotator(0.0, 90.0, 0.0))
    configure_comment(bp, '차량 이동  |  StartBP 화살표 정방향으로 일정 속도 직진 (C++ TrafficCarActor)',
                      (0.10, 0.45, 0.85))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    if not unreal.EditorAssetLibrary.save_loaded_asset(bp):
        raise RuntimeError('Could not save {}'.format(bp_name))
    if not generated:
        raise RuntimeError('Missing generated class {}'.format(bp_name))
    car_classes.append(generated)
    unreal.log_warning('CAR_TRAFFIC_CONFIG car={} mesh={}'.format(bp_name, mesh.get_path_name()))

start_bp = reparent(BASE + 'BP_RoadPathStart', start_parent)
start_cdo = unreal.get_default_object(unreal.load_class(None, BASE + 'BP_RoadPathStart.BP_RoadPathStart_C'))
start_cdo.set_editor_property('car_classes', car_classes)
start_cdo.set_editor_property('min_spawn_interval', 5.0)
start_cdo.set_editor_property('max_spawn_interval', 10.0)
configure_comment(start_bp, '랜덤 차량 스폰  |  서버에서 5~10초마다 7종 중 1대를 화살표 방향으로 생성',
                  (0.10, 0.70, 0.30))
unreal.BlueprintEditorLibrary.compile_blueprint(start_bp)
if not unreal.EditorAssetLibrary.save_loaded_asset(start_bp):
    raise RuntimeError('Could not save StartBP')

end_bp = reparent(BASE + 'BP_RoadPathEnd', end_parent)
configure_comment(end_bp, '차량 제거  |  EndBP 박스 영역에 닿은 교통 차량을 서버에서 제거',
                  (0.82, 0.22, 0.15))
unreal.BlueprintEditorLibrary.compile_blueprint(end_bp)
if not unreal.EditorAssetLibrary.save_loaded_asset(end_bp):
    raise RuntimeError('Could not save EndBP')

unreal.log_warning('CAR_TRAFFIC_CONFIG complete cars={} interval=5-10'.format(len(car_classes)))
