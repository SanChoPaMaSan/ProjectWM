import unreal
unreal.log('REPAR_API {}'.format([x for x in dir(unreal.BlueprintEditorLibrary) if 'parent' in x.lower() or 'reparent' in x.lower()]))
