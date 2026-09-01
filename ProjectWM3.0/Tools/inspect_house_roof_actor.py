import unreal


def log(message):
    unreal.log(f"ROOF_INSPECT|{message}")


if unreal.EditorLoadingAndSavingUtils.load_map("/Game/H/LEVEL/HOUSE"):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            if mesh and mesh.get_name().lower() == "hfloor":
                log(
                    f"ROOF|actor={actor.get_name()}|label={actor.get_actor_label()}|"
                    f"loc={actor.get_actor_location()}|rot={actor.get_actor_rotation()}|"
                    f"scale={actor.get_actor_scale3d()}|mesh={mesh.get_path_name()}|"
                    f"mat0={component.get_material(0).get_path_name() if component.get_material(0) else 'None'}"
                )
else:
    log("HOUSE_LOAD_FAILED")
