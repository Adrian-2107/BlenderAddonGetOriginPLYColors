bl_info = {
    "name": "PLY Farben original herstellen - Adrian Ruf",
    "author": "Adrian Ruf",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Object > PLY Pointcloud Display Adrian Ruf",
    "description": "Convert all imported PLY meshes with vertex colors to crisp pointcloud display using Geometry Nodes + Emission",
    "category": "Object",
}

import bpy


def ensure_material(mat_name: str, attribute_name: str, emission_strength: float) -> bpy.types.Material:
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)

    mat.use_nodes = True

    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (700, 0)

    attr = nodes.new("ShaderNodeAttribute")
    attr.location = (-600, 0)
    attr.attribute_name = attribute_name

    sep = nodes.new("ShaderNodeSeparateColor")
    sep.location = (-350, 0)
    sep.mode = 'RGB'

    comb = nodes.new("ShaderNodeCombineColor")
    comb.location = (-120, 0)
    comb.mode = 'RGB'

    em = nodes.new("ShaderNodeEmission")
    em.location = (250, 0)
    em.inputs["Strength"].default_value = emission_strength

    links.new(attr.outputs["Color"], sep.inputs["Color"])

    links.new(sep.outputs["Red"], comb.inputs["Red"])
    links.new(sep.outputs["Green"], comb.inputs["Green"])
    links.new(sep.outputs["Blue"], comb.inputs["Blue"])

    links.new(comb.outputs["Color"], em.inputs["Color"])
    links.new(em.outputs["Emission"], out.inputs["Surface"])

    return mat


def ensure_geo_nodes_group(group_name: str, mat: bpy.types.Material, point_radius: float) -> bpy.types.NodeTree:
    ng = bpy.data.node_groups.get(group_name)
    if ng is None:
        ng = bpy.data.node_groups.new(group_name, "GeometryNodeTree")
        ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    nodes = ng.nodes
    links = ng.links
    nodes.clear()

    n_in = nodes.new("NodeGroupInput")
    n_in.location = (-500, 0)

    mesh_to_points = nodes.new("GeometryNodeMeshToPoints")
    mesh_to_points.location = (-150, 0)
    mesh_to_points.mode = 'VERTICES'
    mesh_to_points.inputs["Radius"].default_value = point_radius

    set_mat = nodes.new("GeometryNodeSetMaterial")
    set_mat.location = (150, 0)
    set_mat.inputs["Material"].default_value = mat

    n_out = nodes.new("NodeGroupOutput")
    n_out.location = (450, 0)

    links.new(n_in.outputs["Geometry"], mesh_to_points.inputs["Mesh"])
    links.new(mesh_to_points.outputs["Points"], set_mat.inputs["Geometry"])
    links.new(set_mat.outputs["Geometry"], n_out.inputs["Geometry"])

    return ng


def has_color_attribute(obj: bpy.types.Object, attribute_name: str) -> bool:
    if obj.type != "MESH":
        return False

    if not hasattr(obj.data, "color_attributes"):
        return False

    return attribute_name in [ca.name for ca in obj.data.color_attributes]


def apply_pointcloud_display(obj: bpy.types.Object, attribute_name: str, point_radius: float, emission_strength: float):
    if obj.type != "MESH":
        raise RuntimeError(f'Object "{obj.name}" is type {obj.type}, expected MESH.')

    mat = ensure_material("PLY_Col_Emission", attribute_name, emission_strength)
    ng = ensure_geo_nodes_group("PLY_MeshToPoints_SetMat", mat, point_radius)

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    mod = obj.modifiers.get("PLY_PointCloud")
    if mod is None:
        mod = obj.modifiers.new(name="PLY_PointCloud", type='NODES')

    mod.node_group = ng


class OBJECT_OT_ply_pointcloud_display(bpy.types.Operator):
    bl_idname = "object.ply_pointcloud_display_all_adrian_ruf"
    bl_label = "ply original farben wiederherstellen -Adrian Ruf"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ATTRIBUTE_NAME = "Col"
        POINT_RADIUS = 0.001
        EMISSION_STRENGTH = 5.0

        targets = [
            obj for obj in bpy.context.scene.objects
            if has_color_attribute(obj, ATTRIBUTE_NAME)
        ]

        if len(targets) == 0:
            self.report({'ERROR'}, f'Keine Mesh-Objekte mit Farbattribut "{ATTRIBUTE_NAME}" gefunden')
            return {'CANCELLED'}

        applied = []
        failed = []

        for obj in targets:
            try:
                apply_pointcloud_display(
                    obj,
                    attribute_name=ATTRIBUTE_NAME,
                    point_radius=POINT_RADIUS,
                    emission_strength=EMISSION_STRENGTH,
                )
                applied.append(obj.name)
            except Exception as e:
                failed.append(f'{obj.name}: {e}')

        if failed:
            self.report({'WARNING'}, f'Angewendet auf {len(applied)} Objekt(e), Fehler bei: {failed}')
        else:
            self.report({'INFO'}, f'Angewendet auf {len(applied)} Objekt(e): {applied}')

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_ply_pointcloud_display.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_ply_pointcloud_display)
    bpy.types.VIEW3D_MT_object.prepend(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_OT_ply_pointcloud_display)


if __name__ == "__main__":
    register()
