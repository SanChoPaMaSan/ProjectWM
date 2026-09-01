import unreal


def log(message):
    unreal.log(f"LIGHT_INSPECT|{message}")


if unreal.EditorLoadingAndSavingUtils.load_map("/Game/H/LEVEL/HOUSE"):
    min_bound = unreal.Vector(1.0e9, 1.0e9, 1.0e9)
    max_bound = unreal.Vector(-1.0e9, -1.0e9, -1.0e9)
    static_actor_count = 0
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        is_light = bool(actor.get_components_by_class(unreal.LightComponent))
        label = actor.get_actor_label()
        if is_light:
            for component in actor.get_components_by_class(unreal.LightComponent):
                intensity = component.get_editor_property("intensity")
                color = component.get_editor_property("light_color")
                log(
                    f"HOUSE_LIGHT|label={label}|class={component.get_class().get_name()}|"
                    f"loc={component.get_world_location()}|intensity={intensity}|color={color}|"
                    f"mobility={component.get_editor_property('mobility')}"
                )

        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            static_actor_count += 1
            origin, extent = actor.get_actor_bounds(False)
            min_bound.x = min(min_bound.x, origin.x - extent.x)
            min_bound.y = min(min_bound.y, origin.y - extent.y)
            min_bound.z = min(min_bound.z, origin.z - extent.z)
            max_bound.x = max(max_bound.x, origin.x + extent.x)
            max_bound.y = max(max_bound.y, origin.y + extent.y)
            max_bound.z = max(max_bound.z, origin.z + extent.z)
            static_mesh = component.get_editor_property("static_mesh")
            if static_mesh and static_mesh.get_name().lower() == "hfloor":
                origin, extent = actor.get_actor_bounds(False)
                log(
                    f"HOUSE_HFLOOR_BOUNDS|label={label}|origin={origin}|extent={extent}|"
                    f"loc={actor.get_actor_location()}"
                )

        if any(token in label.lower() for token in ("light", "lamp", "ceiling")):
            log(f"HOUSE_POSSIBLE_LAMP|label={label}|loc={actor.get_actor_location()}|class={actor.get_class().get_name()}")
    log(f"HOUSE_STATIC_BOUNDS|components={static_actor_count}|min={min_bound}|max={max_bound}")
else:
    log("HOUSE_LOAD_FAILED")

if unreal.EditorLoadingAndSavingUtils.load_map("/Game/LEVEL/WM"):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(actor, unreal.PostProcessVolume):
            settings = actor.get_editor_property("settings")
            log(
                f"WM_PPV|label={actor.get_actor_label()}|"
                f"method={settings.get_editor_property('auto_exposure_method')}|"
                f"bias={settings.get_editor_property('auto_exposure_bias')}|"
                f"min={settings.get_editor_property('auto_exposure_min_brightness')}|"
                f"max={settings.get_editor_property('auto_exposure_max_brightness')}"
            )
        for component in actor.get_components_by_class(unreal.SkyLightComponent):
            log(
                f"WM_SKYLIGHT|label={actor.get_actor_label()}|intensity={component.get_editor_property('intensity')}|"
                f"mobility={component.get_editor_property('mobility')}"
            )
else:
    log("WM_LOAD_FAILED")
