"""Capture the actual editor viewport at representative map positions.

Run with -ExecutePythonScript, not a commandlet: captures need editor ticks.
Changes to view/blend weights are temporary and are never saved.
"""
from pathlib import Path
import time
import traceback
import unreal

unreal.EditorPythonScripting.set_keep_python_script_alive(True)

OUTPUT = Path(unreal.Paths.project_saved_dir()) / 'ToonReview'
OUTPUT.mkdir(parents=True, exist_ok=True)
exec((Path(__file__).with_name('verify_global_toon.py')).read_text(), globals())
world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = actors.get_all_level_actors()
volume = next(a for a in all_actors if a.get_actor_label() == 'PPV_GlobalToon')
starts = [a for a in all_actors if isinstance(a, unreal.PlayerStart)]
shots = []
for i, start in enumerate(starts[:2]):
    location = start.get_actor_location() + unreal.Vector(0, 0, 100)
    rotation = start.get_actor_rotation()
    shots += [(f'player{i}_off', location, rotation, 0.0),
              (f'player{i}_toon', location, rotation, 1.0)]
houses = [a for a in all_actors if a.get_actor_label() in ['HOUSE', 'HOUSE2']]
if houses:
    target = houses[0].get_actor_location() + unreal.Vector(0, 0, 150)
    location = target + unreal.Vector(-6000, -6000, 3500)
    rotation = unreal.MathLibrary.find_look_at_rotation(location, target)
    shots += [('exterior_off', location, rotation, 0.0), ('exterior_toon', location, rotation, 1.0)]
assert shots, 'No camera references found'
unreal.SystemLibrary.execute_console_command(world, 'r.Streaming.FullyLoadUsedTextures 1')
unreal.SystemLibrary.execute_console_command(world, 'r.ShaderPipelineCache.Enabled 0')
state = {'index': 0, 'phase': 'position', 'next': time.monotonic() + 20.0, 'task': None}

def tick(delta):
    try:
        if time.monotonic() < state['next']:
            return
        if state['index'] >= len(shots):
            unreal.log('TOON_CAPTURE|DONE|' + str(OUTPUT))
            unreal.unregister_slate_post_tick_callback(handle)
            unreal.SystemLibrary.quit_editor()
            return
        name, location, rotation, weight = shots[state['index']]
        if state['phase'] == 'position':
            # Toggle only the toon passes; keep the map's exposure settings.
            settings = volume.get_editor_property('settings')
            weighted = settings.get_editor_property('weighted_blendables')
            entries = list(weighted.get_editor_property('array'))
            for entry in entries:
                if entry.get_editor_property('object').get_name() in ['MI_PP_ToonGlobal', 'MI_PP_ToonOutline']:
                    entry.set_editor_property('weight', weight)
            weighted.set_editor_property('array', entries)
            settings.set_editor_property('weighted_blendables', weighted)
            volume.set_editor_property('settings', settings)
            unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(location, rotation)
            state['phase'] = 'capture'
            state['next'] = time.monotonic() + 12.0
        elif state['phase'] == 'capture':
            state['requested_at'] = time.time()
            state['task'] = unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, str(OUTPUT / (name + '.png')))
            state['phase'] = 'check'
            state['next'] = time.monotonic() + 5.0
        elif ((OUTPUT / (name + '.png')).exists()
              and (OUTPUT / (name + '.png')).stat().st_mtime >= state['requested_at']):
            unreal.log('TOON_CAPTURE|SAVED|' + name)
            state['index'] += 1
            state['phase'] = 'position'
        else:
            raise RuntimeError('Screenshot missing: ' + name)
    except Exception:
        unreal.log_error('TOON_CAPTURE|' + traceback.format_exc())
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.quit_editor()

handle = unreal.register_slate_post_tick_callback(tick)
