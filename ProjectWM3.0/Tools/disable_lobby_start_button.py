import unreal

asset_path = "/Game/UI/WBP_LobbyMenu"
widget_blueprint = unreal.load_asset(asset_path)
if not widget_blueprint:
    raise RuntimeError(f"Could not load {asset_path}")

start_button = unreal.load_object(
    None, "/Game/UI/WBP_LobbyMenu.WBP_LobbyMenu:WidgetTree.StartButton"
)
if not start_button:
    raise RuntimeError("StartButton was not found in WBP_LobbyMenu")

# Safety gate: no client or one-player lobby can start the match until the
# lobby controller later enables this button after validating the host/player count.
start_button.set_editor_property("is_enabled", False)

unreal.EditorAssetLibrary.save_loaded_asset(widget_blueprint)
unreal.log("WBP_LobbyMenu StartButton default set to disabled.")
