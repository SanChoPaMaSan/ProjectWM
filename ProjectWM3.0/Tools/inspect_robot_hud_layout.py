import unreal

widget = unreal.load_object(None, '/Game/UI/WBP_RobotHUD.WBP_RobotHUD:WidgetTree')
if not widget:
    raise RuntimeError('WBP_RobotHUD WidgetTree not found')

for child in widget.get_editor_property('all_widgets'):
    slot = child.slot
    details = []
    if slot:
        for name in ('anchors', 'alignment', 'position', 'size', 'offsets'):
            try:
                details.append('{}={}'.format(name, slot.get_editor_property(name)))
            except Exception:
                pass
    unreal.log_warning('HUD_LAYOUT|name={}|class={}|slot={}'.format(
        child.get_name(), child.get_class().get_name(), '|'.join(details)))
