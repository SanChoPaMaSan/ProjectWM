import unreal


def log(message):
    unreal.log(f"INDOOR_LIGHT_VERIFY|{message}")


light_count = 0
bad_lights = 0
if unreal.EditorLoadingAndSavingUtils.load_map("/Game/H/LEVEL/HOUSE"):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if not actor.get_actor_label().startswith("IndoorFillLight_"):
            continue
        light_count += 1
        components = actor.get_components_by_class(unreal.PointLightComponent)
        component = components[0] if components else None
        is_ok = bool(component) and component.get_editor_property("intensity") == 2800.0 and component.get_editor_property("attenuation_radius") == 1250.0
        if not is_ok:
            bad_lights += 1
        log(
            f"LIGHT|label={actor.get_actor_label()}|ok={is_ok}|"
            f"loc={actor.get_actor_location()}|intensity={component.get_editor_property('intensity') if component else 'None'}|"
            f"radius={component.get_editor_property('attenuation_radius') if component else 'None'}"
        )
else:
    bad_lights += 6
    log("HOUSE_LOAD_FAILED")

ppv_ok = False
if unreal.EditorLoadingAndSavingUtils.load_map("/Game/LEVEL/WM"):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() != "PPV_GlobalToon":
            continue
        settings = actor.get_editor_property("settings")
        method = settings.get_editor_property("auto_exposure_method")
        bias = settings.get_editor_property("auto_exposure_bias")
        physical = settings.get_editor_property("auto_exposure_apply_physical_camera_exposure")
        ppv_ok = method == unreal.AutoExposureMethod.AEM_MANUAL and bias == 0.0 and not physical
        log(f"PPV|ok={ppv_ok}|method={method}|bias={bias}|physical={physical}")
        break
else:
    log("WM_LOAD_FAILED")

log(f"SUMMARY|lights={light_count}|bad_lights={bad_lights}|ppv_ok={ppv_ok}")
