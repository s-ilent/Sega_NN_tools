from Sega_NN_tools.modules.blender.model import *
from Sega_NN_tools.modules.game_specific.srpc.block_type_check import BlockTypeCheck
from Sega_NN_tools.modules.game_specific.srpc.extract_image import ExtractImage
from Sega_NN_tools.modules.game_specific.srpc.read_archive import read_archive
from Sega_NN_tools.modules.nn.nn import ReadNn
from Sega_NN_tools.modules.util import *


class ReadSRPC:
    def __init__(self, f, file_path, settings):
        self.f = f
        self.file_path = file_path
        self.settings = settings
        self.sub_file_offsets = None
        self.sub_file_data = []
        self.texture_name_list = [False]
        self.image_block_14 = None
        self.material_in_next_block = []
        self.tex_block_index = 0

    def execute(self):
        def toggle():
            if self.settings.batch_import == "Single" and file_count > 10:
                toggle_console()
        archive = read_archive(self.f)  # read the files archive data
        file_count = archive.file_count
        self.sub_file_offsets = archive.sub_file_offsets
        toggle()

        cur_count = 0
        for file_index in range(file_count):
            print("Reading a file------------------------------------")
            print(" " * 49, "| Reading file", file_index + 1, "of", file_count)
            for _ in range(archive.sub_file_counts[file_index]):
                print("Reading a sub file--------------------------------")
                if self.sub_file_offsets[cur_count]:  # seek 0 happens sometimes
                    self.f.seek(self.sub_file_offsets[cur_count])  # seek first file
                    self.read_sub(cur_count)
                else:
                    print("Skipping Null Block (File offset is 0)")
                cur_count += 1
            print("Making sub files in blender-----------------------")
            print(" " * 49, "| Making file", file_index + 1, "of", file_count)
            self.make_subs()
            self.sub_file_data = []
            if self.image_block_14 and self.material_in_next_block:
                for mat in self.material_in_next_block:
                    print("Adding out of block textures to materials...")
                    for mat_tex_index, new_node, inp, oup, n_tree in mat:
                        new_node.image = self.image_block_14[mat_tex_index]
                        n_tree.links.new(inp, oup)
                self.material_in_next_block = []
        toggle()

    def read_sub(self, cur_count):
        f = self.f
        sub_file_data = self.sub_file_data

        block_name = read_str(f, 4)

        if block_name == 'NXIF':  # determine if file or image
            f.seek(-4, 1)
            __, nn_data = ReadNn(f, self.file_path, self.settings.format, self.settings.debug).read_file()
            if nn_data.texture_names:
                nxtl_block = 1
            else:
                nxtl_block = - self.tex_block_index
            sub_file_data.append([nn_data, nxtl_block + self.tex_block_index])

        else:  # check and extract textures
            if len(self.sub_file_offsets) > cur_count + 1:
                next_b = self.sub_file_offsets[cur_count + 1]
            else:
                next_b = os.path.getsize(self.file_path)
            if self.settings.import_all_formats:
                block_type = BlockTypeCheck(f, self.file_path, next_b).execute()
            else:
                block_type = BlockTypeCheck(f, self.file_path, next_b).check_image()
            if block_type:  # returns true if textures
                time_s = console_out_pre("Extracting textures...")
                texture_name_list, _, _,  type_byte = \
                    ExtractImage(f, self.file_path, self.settings.texture_name_structure, cur_count).execute()
                if type_byte == 20:
                    self.image_block_14 = texture_name_list
                self.texture_name_list.append(texture_name_list)
                self.tex_block_index += 1
                console_out_post(time_s)

    def make_subs(self):
        texture_name_list = self.texture_name_list
        for s_file in self.sub_file_data:
            s_data, s_extra = s_file
            if s_data.model_data:
                if s_extra >= len(texture_name_list):  # fix this ?
                    s_extra = -1
                obj_make_start = time()
                s_data.texture_names = texture_name_list[s_extra]
                self.material_in_next_block.append(Model(s_data, self.settings).execute())
                print(" " * 49, "| Overall %f seconds" % (time() - obj_make_start))
            else:  # anims here when done
                print(" " * 49, "| Skipping unsupported block")
