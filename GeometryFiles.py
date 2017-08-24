# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import os, time


class GeoFile:
    def __init__(self, file_name, message_func=print):
        self.message_func = message_func
        self.file_name = file_name
        self.loaded = False

        # initialise progress counters
        self.progress = 0
        self.progress_total = 0
        self.cached = False

        # declare variables
        self.num_elements = None
        self.face_nodes = None
        self.multi_mesh_face_index = None
        self.face2patch = None
        self.patch2face = None
        self.x = None
        self.elemFaces = None
        self.materialElem = None
        self.elem2patch = None
        self.patch2elem = None
        self.adjElem = []
        self.facePatches = None

    def load(self):
        # if already loaded, do nothin
        if self.loaded:
            return True

        # if a cache file exists, load from the cache file
        if self.load_cache_if_exists():
            self.message_func('File loaded from cache...')
            return True

        # if needs loading, load from .geo file
        with open(self.file_name) as file:
            ver, num_nodes, num_faces, self.num_elements = map(int, file.readline().split())

            self.progress_total = num_nodes + num_faces + self.num_elements * 2

            self.message_func('Reading nodes...')

            self.x = np.empty((num_nodes, 3))
            for iNode in range(num_nodes):
                tmp = file.readline().split()
                self.x[iNode, :] = list(map(float, tmp[0:3]))
                self.progress += 1

            self.message_func('Reading faces...')

            self.face_nodes = []
            self.multi_mesh_face_index = np.empty(num_faces, dtype=int)
            self.face2patch = np.empty(num_faces, dtype=int)
            self.patch2face = np.empty(num_faces, dtype=int)

            for iFace in range(num_faces):
                num_vertices_face = int(file.readline())
                tmp = file.readline().split()
                temp_vertices = list(map(int, tmp[0:num_vertices_face]))
                temp_vertices = [x - 1 for x in temp_vertices]
                self.face_nodes.append(temp_vertices)
                self.multi_mesh_face_index[iFace] = int(tmp[num_vertices_face])
                self.face2patch[iFace] = int(tmp[num_vertices_face+1])
                self.patch2face[self.face2patch[iFace]] = iFace
                self.progress += 1

            self.message_func('Reading elements...')

            self.elemFaces = []
            self.materialElem = np.empty(self.num_elements, dtype=int)
            self.elem2patch = np.empty(self.num_elements, dtype=int)
            self.patch2elem = np.empty(self.num_elements, dtype=int)

            num_faces_elements = np.empty(self.num_elements, dtype=int)
            for iElem in range(self.num_elements):
                num_faces_element = int(file.readline())
                tmp = file.readline().split()

                elem_faces_tmp = list(map(int, tmp[0:num_faces_element]))
                elem_faces_tmp = [x - 1 for x in elem_faces_tmp]
                self.elemFaces.append(elem_faces_tmp)
                self.materialElem[iElem] = int(tmp[num_faces_element])
                self.elem2patch[iElem] = int(tmp[num_faces_element+1])
                self.patch2elem[self.elem2patch[iElem]] = iElem
                num_faces_elements[iElem] = num_faces_element
                self.progress += 1

            self.message_func('Reading adjacency...')
            self.adjElem = []
            for iElem in range(self.num_elements):
                tmp = file.readline().split()
                tmp = list(map(int, tmp[0:num_faces_elements[iElem]]))
                tmp = [x - 1 for x in tmp]
                self.adjElem.append(tmp)
                self.progress += 1

            self.facePatches = np.unique(self.face2patch)
            # remove facePatch 0 (since this refers to no patch)
            self.facePatches = self.facePatches[1:]

            self.loaded = True

    def cache(self):
        if self.cached:
            return
        self.message_func("Caching...")
        np.savez_compressed(self.file_name,
                            num_elements=self.num_elements,
                            face2patch=self.face2patch,
                            patch2face=self.patch2face,
                            x=self.x,
                            elemFaces=self.elemFaces,
                            materialElem=self.materialElem,
                            adjElem=self.adjElem,
                            elem2patch=self.elem2patch,
                            patch2elem=self.patch2elem,
                            face_nodes=self.face_nodes,
                            facePatches=self.facePatches)
        self.cached = True
        self.message_func("Cached")

    def load_cache_if_exists(self):
        cache_file_name = "%s.npz" % self.file_name

        if not os.path.isfile(cache_file_name):
            return False
        else:
            self.load_from_cache_file(cache_file_name)
            return True

    def load_from_cache_file(self, file_name):
            saved = np.load(file_name)
            self.progress_total = len(saved.keys())
            self.progress = 0

            for key in saved.keys():
                if not key == 'adjElem':
                    # adjElem not loaded since it isn't used
                    self.__setattr__(key, saved[key])
                self.progress += 1

            self.cached = True
            self.loaded = True
            '''
            typical load times:
                num_elements  0.31
                face_nodes  9.63
                multi_mesh_face_index  0.11
                face2patch  0.11
                patch2face  0.11
                x  0.44
                elemFaces  3.10
                materialElem  0.03
                elem2patch  0.029
                patch2elem  0.03
                adjElem  3.09
                facePatches  0.01
            '''


class Geom:
    def __init__(self, geo_file):
        self.geo = GeoFile(geo_file)
        self.patchFaceNodes = dict({})
        self.num_faces_per_patch = None

    def load(self):
        self.geo.load()
    
    def get_face_patches(self):
        return self.geo.facePatches

    def get_count_face_patches(self):
        self.geo.load()

        if self.num_faces_per_patch is not None:
            return self.num_faces_per_patch

        n_faces_per_patch = dict({})
        for index in self.geo.facePatches:
            faces = np.where(self.geo.face2patch == index)
            if len(faces) > 0:
                n_faces_per_patch[index] = len(faces[0])
            else:
                n_faces_per_patch[index] = 0

        self.num_faces_per_patch = n_faces_per_patch
        return self.num_faces_per_patch

    def get_patch_lines(self, patches, color=None, label=None,
                        rotation=None, linestyle='-', linewidth=1.0):
        self.geo.load()

        # plot all lines and add rotation if necessary
        l = []
        for iPatch in patches:
            nodes = self.getNodesPatch(iPatch)

            for lineNodes in nodes:
                Xplot = self.geo.x[lineNodes, :2]
                if rotation:
                    theta = np.deg2rad(rotation)
                    RotOp = np.array([[np.cos(theta), - np.sin(theta)],
                                      [np.sin(theta), np.cos(theta)]])
                    Xplot = Xplot.dot(RotOp)
                l.extend(plt.plot(Xplot[:, 0], Xplot[:, 1], color=color,
                                  linewidth=linewidth, linestyle=linestyle))

        l[0].set_label(label)

        plt.axis('equal')

        return l

    def get_patch_faces(self, patches, color=None, label=None,
                        rotation=None, linestyle='-', linewidth=1.0, polar=False, plot=False):
        self.geo.load()

        l = []
        x = []
        y = []
        for iPatch in patches:
            nodes = self.get_nodes_patches_as_lines(iPatch)

            if not color:
                cmap = plt.get_cmap('jet_r')

                N = np.max(self.geo.face2patch)

                color = cmap(iPatch/N)
                label = 'Patch %d' % iPatch

            for lineNodes in nodes:
                Xplot = self.geo.x[lineNodes, :2]
                if rotation is not None:
                    theta = np.deg2rad(rotation)
                    RotOp = np.array([[np.cos(theta), -np.sin(theta)],
                                      [np.sin(theta),  np.cos(theta)]])
                    Xplot = Xplot.dot(RotOp)
                
                if polar:
                    xtmp = np.arctan2(Xplot[:, 0], Xplot[:, 1])
                    ytmp = np.sqrt(Xplot[:, 0]**2 + Xplot[:, 1]**2)
                    Xplot[:, 0] = xtmp
                    Xplot[:, 1] = ytmp
                x.extend(Xplot[:, 0])
                y.extend(Xplot[:, 1])
                x.append(np.NaN)
                y.append(np.NaN)
                if plot:
                    l.extend(plt.plot(Xplot[:, 0], Xplot[:, 1], color=color, linewidth=linewidth, linestyle=linestyle))

        if plot:
            l[0].set_label(label)
            plt.axis('equal')
            return l
        else:
            return x, y

    def get_patch_coords(self, patch_index):
        return self.geo.x[self.getPatchNodes(patch_index), :2]

    def getPatchNodes(self, patch_index):
        self.geo.load()

        if patch_index not in self.geo.facePatches:
            raise ValueError('Face patch %d was not found' % patch_index)

        node_list = []
        plot_lines = [node_list]
        self.patchFaceNodes[patch_index] = plot_lines

        faces = np.where(self.geo.face2patch == patch_index)
        faces = faces[0]

        face_nodes = np.empty([len(faces), 2], dtype='int')
        for iFace in range(len(faces)):
            face_nodes[iFace, :] = self.geo.face_nodes[faces[iFace]][0:2]

        return np.array(face_nodes)

    # gets the nodes for a given patch, returns them as coordinates points of
    # connected lines, for use with plotting software such as matplotlib

    def get_nodes_coords_as_lines(self, patch_index):
        self.geo.load()

        nodes_as_lines = self.get_nodes_patches_as_lines(patch_index)
        
        if len(nodes_as_lines) == 1:
            return self.geo.x[nodes_as_lines, :2][0]
        else:
            return [self.geo.x[nodesAsLine, :2][0] for nodesAsLine in nodes_as_lines]

    def get_nodes_patches_as_lines(self, patch_index, join=True):
        self.geo.load()

        if patch_index not in self.geo.facePatches:
            raise ValueError('Face patch %d was not found' % patch_index)

        node_list = []
        plot_lines = [node_list]
        do_init = True
        self.patchFaceNodes[patch_index] = plot_lines

        faces = np.where(self.geo.face2patch == patch_index)
        faces = faces[0]

        for iFace in faces:
            node_left = self.geo.face_nodes[iFace][0]
            node_right = self.geo.face_nodes[iFace][1]

            # join faces together on the fly if possible...
            if do_init:
                node_list.extend([node_left, node_right])
                do_init = False
            else:
                if node_list[0] == node_left:
                    node_list.insert(0, node_right)
                elif node_list[-1] == node_left:
                    node_list.append(node_right)
                elif node_list[0] == node_right:
                    node_list.insert(0, node_left)
                elif node_list[-1] == node_right:
                    node_list.append(node_left)
                else:
                    # if faces can't be joined on the fly, then add
                    # a new "line" and merge lines later
                    node_list = [node_left, node_right]
                    self.patchFaceNodes[patch_index].append(node_list)

        # sweep all faces and join lines together...
        if join:
            number_changed = 100
            while number_changed > 0:
                number_changed = 0

                i = 0
                while i < len(plot_lines):
                    delete_lines = []

                    for j in range(i+1, len(plot_lines)):
                        if plot_lines[i][-1] == plot_lines[j][0]:
                            plot_lines[i].extend(plot_lines[j][1:])
                            delete_lines.append(j)
                        elif plot_lines[i][-1] == plot_lines[j][-1]:
                            plot_lines[j].reverse()
                            plot_lines[i].extend(plot_lines[j][1:])
                            delete_lines.append(j)
                        elif plot_lines[i][0] == plot_lines[j][0]:
                            plot_lines[i].reverse()
                            plot_lines[i].extend(plot_lines[j][1:])
                            delete_lines.append(j)
                        elif plot_lines[i][0] == plot_lines[j][-1]:
                            plot_lines[i].reverse()
                            plot_lines[j].reverse()
                            plot_lines[i].extend(plot_lines[j][1:])
                            delete_lines.append(j)

                    number_changed += len(delete_lines)

                    for delLine in sorted(delete_lines, reverse=True):
                        del plot_lines[delLine]

                    i += 1

            return plot_lines

    def blade_radius(self, blade_patches):
        self.geo.load()

        max_radius = 0
        color = 'red'

        for iPatch in blade_patches:
            faces = np.where(self.geo.face2patch == iPatch)
            faces = faces[0]

            for iFace in faces:
                nodes = self.geo.face_nodes[iFace]
                x_plot = self.geo.x[nodes, 0:2]

                max_face = np.sqrt(np.sum([x**2 for x in x_plot]))

                if max_face > max_radius:
                    max_radius = max_face

                plt.plot(x_plot[:, 0], x_plot[:, 1], '-', c=color)

                plt.axis('equal')
