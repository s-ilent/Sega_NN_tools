import bpy


class Collection:
    def make_collection(self):
        collection = bpy.data.collections.new(self.model_name)
        bpy.context.scene.collection.children.link(collection)
        # NOTE the use of 'collection.name' to account for potential automatic renaming
        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection