import bpy
import json
import os


images = []
for image in bpy.data.images:
    if image.source != "FILE":
        continue
    path = bpy.path.abspath(image.filepath) if image.filepath else ""
    images.append({
        "name": image.name,
        "relative_path": image.filepath,
        "path": path,
        "packed": bool(image.packed_file) or bool(getattr(image, "packed_files", [])),
        "exists": bool(path and os.path.exists(path)),
    })

materials = []
for material in bpy.data.materials:
    image_nodes = []
    if material.node_tree:
        for node in material.node_tree.nodes:
            if node.type != "TEX_IMAGE" or not node.image:
                continue
            destinations = []
            for output in node.outputs:
                for link in output.links:
                    destinations.append(f"{link.to_node.name}.{link.to_socket.name}")
            image_nodes.append({"image": node.image.name, "destinations": destinations})
    materials.append({
        "name": material.name,
        "images": image_nodes,
    })

objects = {
    obj.name: [slot.material.name if slot.material else None for slot in obj.material_slots]
    for obj in bpy.data.objects if obj.type == "MESH"
}

print("LASTH_MAP_BEGIN")
print(json.dumps({"images": images, "materials": materials, "objects": objects}, ensure_ascii=False, indent=2))
print("LASTH_MAP_END")
