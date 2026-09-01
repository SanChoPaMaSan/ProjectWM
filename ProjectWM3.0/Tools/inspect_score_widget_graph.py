import unreal

unreal.log('SCORE_API {}'.format([name for name in dir(unreal.BlueprintEditorLibrary) if 'graph' in name.lower()]))

def log_graph(label, graph):
    if not graph:
        return
    unreal.log('SCORE_GRAPH {} graph={}'.format(label, graph.get_name()))
    unreal.log('SCORE_GRAPH {} graph_api={}'.format(label, [name for name in dir(graph) if 'node' in name.lower()]))
    try:
        nodes = graph.get_editor_property('nodes')
    except Exception as exc:
        unreal.log_warning('SCORE_GRAPH {} nodes failed {}'.format(label, exc))
        return
    for node in nodes:
        try:
            title = unreal.BlueprintEditorLibrary.get_node_title(node)
        except Exception:
            title = node.get_name()
        pin_rows = []
        try:
            for pin in node.get_editor_property('pins'):
                name = str(pin.get_editor_property('pin_name'))
                default = str(pin.get_editor_property('default_value'))
                links = [str(link.get_editor_property('pin_name')) for link in pin.get_editor_property('linked_to')]
                pin_rows.append('{}={} links={}'.format(name, default, links))
        except Exception:
            pass
        haystack = '{} {} {}'.format(node.get_name(), title, ' '.join(pin_rows)).lower()
        if any(word in haystack for word in ['score', 'team', 'house', 'player', 'trash', 'text']):
            unreal.log('SCORE_NODE {} {} title={} pins={}'.format(label, node.get_name(), title, ' | '.join(pin_rows)))

for label, path in [
    ('HUD', '/Game/UI/WBP_RobotHUD'),
    ('DELIVERY', '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'),
]:
    bp = unreal.load_asset(path)
    if not bp:
        unreal.log_error('SCORE_GRAPH {} missing {}'.format(label, path))
        continue
    unreal.log('SCORE_GRAPH {} names={}'.format(label, unreal.BlueprintEditorLibrary.list_graph_names(bp)))
    try:
        unreal.log('SCORE_GRAPH {} list_graphs={}'.format(label, [graph.get_name() for graph in unreal.BlueprintEditorLibrary.list_graphs(bp)]))
        for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
            log_graph(label, graph)
    except Exception as exc:
        unreal.log_warning('SCORE_GRAPH {} list_graphs failed {}'.format(label, exc))
    for graph_name in unreal.BlueprintEditorLibrary.list_graph_names(bp):
        try:
            graph = unreal.BlueprintEditorLibrary.find_graph(bp, graph_name)
            log_graph(label, graph)
        except Exception as exc:
            unreal.log_warning('SCORE_GRAPH {} find {} failed {}'.format(label, graph_name, exc))
    try:
        log_graph(label, unreal.BlueprintEditorLibrary.find_event_graph(bp))
    except Exception as exc:
        unreal.log_warning('SCORE_GRAPH {} event graph failed {}'.format(label, exc))
    seen = set()
    for prop_name in ['ubergraph_pages', 'function_graphs', 'macro_graphs']:
        try:
            graphs = bp.get_editor_property(prop_name)
        except Exception as exc:
            unreal.log_warning('SCORE_GRAPH {} {} failed {}'.format(label, prop_name, exc))
            continue
        for graph in graphs:
            if graph and graph.get_path_name() not in seen:
                seen.add(graph.get_path_name())
                log_graph(label, graph)
