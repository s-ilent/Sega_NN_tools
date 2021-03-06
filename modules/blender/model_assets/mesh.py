import bpy


class Mesh:
    def make_mesh(self):
        bone_groups = self.bone_groups
        model_name = self.model_name
        model_name_strip = self.model_name_strip
        build_mesh1 = self.model_data.build_mesh
        mesh_info = self.model_data.mesh_info
        vertex_data = self.model_data.vertices
        face_list1 = self.model_data.faces
        mesh_names = self.mesh_names
        obj_list = self.obj_list
        material_list_blender = self.material_list_blender
        bone_names = self.bone_names
        armature = self.armature
        b_group = bone_groups
        collection = bpy.context.collection

        def build_mesh():
            def make_uvs():
                if uv_short_hand:
                    uv_tex = mesh.uv_layers.new(name=model_name_strip + "_UV_Map")
                    for vert_index in range(v_loop_count):
                        v_index = vert_index * 3
                        uv_tex.data[v_index].uv = uv_short_hand[face_list[vert_index][0]]
                        uv_tex.data[v_index + 1].uv = uv_short_hand[face_list[vert_index][1]]
                        uv_tex.data[v_index + 2].uv = uv_short_hand[face_list[vert_index][2]]

                    if wx_short_hand:
                        wx_tex = mesh.uv_layers.new(name=model_name_strip + "_WX_Map")
                        for vert_index in range(v_loop_count):
                            v_index = vert_index * 3
                            wx_tex.data[v_index].uv = wx_short_hand[face_list[vert_index][0]]
                            wx_tex.data[v_index + 1].uv = wx_short_hand[face_list[vert_index][1]]
                            wx_tex.data[v_index + 2].uv = wx_short_hand[face_list[vert_index][2]]

            def make_colours():
                col_layer = mesh.vertex_colors.new(name=model_name_strip + "_Vertex_Colours")  # keep for materials
                if col_short_hand:
                    for vert_index in range(v_loop_count):
                        v_index = vert_index * 3
                        col_layer.data[v_index].color = col_short_hand[face_list[vert_index][0]]
                        col_layer.data[v_index + 1].color = col_short_hand[face_list[vert_index][1]]
                        col_layer.data[v_index + 2].color = col_short_hand[face_list[vert_index][2]]

            def make_normals():
                if norm_short_hand:
                    mesh.normals_split_custom_set_from_vertices(norm_short_hand)
                    mesh.use_auto_smooth = True

            def make_weights():
                def single():
                    obj.vertex_groups.new(name=bone_names[b_group.index(sm.bone)])
                    obj.vertex_groups[0].add(list(range(vertex_count)), 1, "REPLACE")

                def multi():
                    weights_main = v_data.weights
                    for bone in m_info.bone_list_complex:
                        obj.vertex_groups.new(name=bone_names[b_group.index(bone)])
                    for vertex_index in range(vertex_count):  # for each vert
                        if v_data.bone_list_indices:
                            w_ind = weights_main[vertex_index]
                            for var in range(len(w_ind)):  # for all the bones
                                b_complex_index = v_data.bone_list_indices[vertex_index][var]
                                weight = w_ind[var]
                                obj.vertex_groups[b_complex_index].add([vertex_index], weight, "ADD")
                        else:  # bone indices arent stored in the vertex block
                            b_count = m_info.bone_count_complex
                            for b_complex_index in range(b_count):  # for all the bones
                                weight = weights_main[vertex_index][b_complex_index]
                                obj.vertex_groups[b_complex_index].add([vertex_index], weight, "REPLACE")
                                # mesh, vertex, weight

                if m_info.bone_count_complex:
                    multi()
                else:
                    single()

            mesh = bpy.data.meshes.new(mesh_names[i])  # add the new mesh
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj_list.append(obj)
            collection.objects.link(obj)
            # mesh.from_pydata(pos_short_hand, [], [])
            mesh.from_pydata(pos_short_hand, [], face_list)
            # mesh.validate(verbose=True)
            obj.data.materials.append(material_list_blender[sm.material])
            make_uvs()
            make_colours()
            make_normals()
            make_weights()
            obj.modifiers.new(name=model_name, type='ARMATURE').object = obj.parent = armature  # add mesh to armature

        for i in range(len(build_mesh1)):  # for each sub mesh
            sm = build_mesh1[i]
            sm_mesh_index = sm.vertex
            m_info = mesh_info[sm_mesh_index]
            v_data = vertex_data[sm_mesh_index]
            face_list = face_list1[sm.face].faces
            vertex_count = len(v_data.positions)

            v_loop_count = len(face_list)
            uv_short_hand = v_data.uvs
            wx_short_hand = v_data.wxs
            col_short_hand = v_data.colours
            norm_short_hand = v_data.normals
            pos_short_hand = v_data.positions

            build_mesh()

            if v_data.normals2:
                norm_short_hand = v_data.normals2
                build_mesh()
                if v_data.normals3:
                    norm_short_hand = v_data.normals3
                    build_mesh()
        return obj_list
