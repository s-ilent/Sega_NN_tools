import bpy


class Armature:
    def make_bones_type_1(self):
        bone_count = self.model_data.data.bone_count
        bone_data = self.model_data.bones
        bone_names = self.bone_names
        max_len = self.settings.max_bone_length
        armature = bpy.context.object.data
        tail_var = self.settings.format_bone_scale

        for i in range(bone_count):
            b = bone_data[i]
            bone = armature.edit_bones.new(bone_names[i])
            if b.parent != 65535:
                bone.parent = armature.edit_bones[b.parent]
            bone.tail = b.relative  # they store the position relative to parent bone
            bone.transform(b.position)  # this isn't the correct usage for b relative but it looks nice!
            if not 0.0001 < bone.length < tail_var * max_len:
                bone.length = tail_var  # len too small = bone isn't made, len too big = can't see anything in blender
            bone.roll = 0

        if self.settings.all_bones_one_length:
            for bone in armature.edit_bones:
                bone.length = tail_var

    def make_armature(self):
        bpy.ops.object.add(type="ARMATURE", enter_editmode=True)  # first we make an armature
        obj = bpy.context.object
        obj.name = obj.data.name = self.model_name  # Object name, Armature name
        obj.rotation_euler[0] = 1.5708  # rotate to stand up
        self.armature = obj

    @staticmethod
    def hide_null_bones():  # in riders these have no weights - 06 has unweighted but they don't have the group
        pose = bpy.context.object.pose
        if "Null_Bone_Group" in pose.bone_groups:
            pose.bone_groups.active = pose.bone_groups["Null_Bone_Group"]
            bpy.ops.pose.group_select()
            bpy.ops.pose.hide(unselected=False)

    def scale_bones(self):
        bone_count = self.model_data.data.bone_count
        bone_data = self.model_data.bones
        pose = bpy.context.object.pose
        for i in range(bone_count):
            bpy.context.object.data.bones[i].inherit_scale = 'NONE'
            pose.bones[i].scale = bone_data[i].scale

    def make_bone_groups(self):
        bone_count = self.model_data.data.bone_count
        bone_data = self.model_data.bones
        group_names = self.group_names
        pose = bpy.context.object.pose
        if self.model_name_strip + "_Bone_Group_" + "65535" in group_names:
            no_weights = pose.bone_groups.new(name="Null_Bone_Group")
            no_weights.color_set = "THEME08"  # makes it clearer

        for i in range(bone_count):
            bone = pose.bones[i]
            if bone_data[i].group != 65535:  # bone has weights
                bone.bone_group = pose.bone_groups.new(name=group_names[i])
            else:  # bone doesn't have weights
                bone.bone_group = no_weights
