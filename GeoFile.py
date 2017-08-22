# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt


def default_progress_inc_func(progress):
    pass

def default_progress_init_func(total_progress):
    pass

class GeoFile:
    def __init__(self, fileName):
        self.fileName = fileName
        self.loaded = False

    def read(self, progress_init_func=default_progress_init_func, progress_inc_func=default_progress_inc_func, message_func=print):
        if not self.loaded:
            with open(self.fileName) as fileobj:
                ver, nNodes, nFaces, self.nElems = map(int, fileobj.readline().split())

                progress_init_func(nNodes + nFaces + self.nElems*2)

                message_func('Reading nodes...')
                self.x = np.empty((nNodes, 3))
                for iNode in range(nNodes):
                    tmp = fileobj.readline().split()
                    self.x[iNode, :] = list(map(float, tmp[0:3]))
                    progress_inc_func()

                message_func('Reading faces...')

                self.faceNodes = []
                self.multiMeshFaceIndex = np.empty(nFaces, dtype=int)
                self.face2patch = np.empty(nFaces, dtype=int)
                self.patch2face = np.empty(nFaces, dtype=int)

                for iFace in range(nFaces):
                    nVerticesFace = int(fileobj.readline())
                    tmp = fileobj.readline().split()
                    tmpVertices = list(map(int, tmp[0:nVerticesFace]))
                    tmpVertices = [x - 1 for x in tmpVertices]
                    self.faceNodes.append(tmpVertices)
                    self.multiMeshFaceIndex[iFace] = int(tmp[nVerticesFace])
                    self.face2patch[iFace] = int(tmp[nVerticesFace+1])
                    self.patch2face[self.face2patch[iFace]] = iFace
                    progress_inc_func()

                message_func('Reading elements...')

                self.elemFaces = []
                self.materialElem = np.empty(self.nElems, dtype=int)
                self.elem2patch = np.empty(self.nElems, dtype=int)
                self.patch2elem = np.empty(self.nElems, dtype=int)

                for iElem in range(self.nElems):
                    nFacesElem = int(fileobj.readline())
                    tmp = fileobj.readline().split()

                    elemFacesTmp = list(map(int, tmp[0:nFacesElem]))
                    elemFacesTmp = [x - 1 for x in elemFacesTmp]
                    self.elemFaces.append(elemFacesTmp)
                    self.materialElem[iElem] = int(tmp[nFacesElem])
                    self.elem2patch[iElem] = int(tmp[nFacesElem+1])
                    self.patch2elem[self.elem2patch[iElem]] = iElem
                    progress_inc_func()

                message_func('Reading adjacency...')
                self.adjElem = []
                for iElem in range(self.nElems):
                    tmp = fileobj.readline().split()
                    tmp = list(map(int, tmp[0:nFacesElem]))
                    tmp = [x - 1 for x in tmp]
                    self.adjElem.append(tmp)
                    progress_inc_func()

                self.facePatches = np.unique(self.face2patch)
                # remove facePatch 0 (since this refers to no patch)
                self.facePatches = self.facePatches[1:]

                self.loaded = True


class Geom:
    def __init__(self, geoFileName):
        self.geo = GeoFile(geoFileName)
        self.patchFaceNodes = dict({})
    
    def get_face_patches(self):
        return self.geo.facePatches

    def getPatchFaceLinesCoords(self, patches, color=None, label=None,
                                rotation=None, linestyle='-', linewidth=1.0):
        self.geo.read()
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

    # plot faces with matplotlib
    def getPatchFaces(self, patches, color=None, label=None,
                      rotation=None, linestyle='-', linewidth=1.0, polar=False, plot=False):
        l = []
        x = []
        y = []
        for iPatch in patches:
            nodes = self.getNodesPatchesAsLines(iPatch)

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

    def getPatchCoords(self, iPatch):
        return self.geo.x[self.getPatchNodes(iPatch), :2]

    def getPatchNodes(self, iPatch):
        self.geo.read()

        if iPatch not in self.geo.facePatches:
            raise ValueError('Face patch %d was not found' % iPatch)

        nodeList = []
        plotLines = [nodeList]
        self.patchFaceNodes[iPatch] = plotLines

        faces = np.where(self.geo.face2patch == iPatch)
        faces = faces[0]

        faceNodes = np.empty([len(faces), 2], dtype='int')
        for iFace in range(len(faces)):
            faceNodes[iFace, :] = self.geo.faceNodes[faces[iFace]][0:2]

        return np.array(faceNodes)

    # gets the nodes for a given patch, returns them as coordinates points of
    # connected lines, for use with plotting software such as matplotlib

    def getNodesCoordsAsLines(self, iPatch):
        nodesAsLines = self.getNodesPatchesAsLines(iPatch)
        
        if len(nodesAsLines) == 1:
            return self.geo.x[nodesAsLines, :2][0]
        else:
            return [self.geo.x[nodesAsLine, :2][0] for nodesAsLine in nodesAsLines]

    def getNodesPatchesAsLines(self, iPatch, join=True):
        self.geo.read()

        if iPatch not in self.geo.facePatches:
            raise ValueError('Face patch %d was not found' % iPatch)

        nodeList = []
        plotLines = [nodeList]
        doinit = True
        self.patchFaceNodes[iPatch] = plotLines

        faces = np.where(self.geo.face2patch == iPatch)
        faces = faces[0]

        for iFace in faces:
            nodeL = self.geo.faceNodes[iFace][0]
            nodeR = self.geo.faceNodes[iFace][1]

            # join faces together on the fly if possible...
            if doinit:
                nodeList.extend([nodeL, nodeR])
                doinit = False
            else:
                if nodeList[0] == nodeL:
                    nodeList.insert(0, nodeR)
                elif nodeList[-1] == nodeL:
                    nodeList.append(nodeR)
                elif nodeList[0] == nodeR:
                    nodeList.insert(0, nodeL)
                elif nodeList[-1] == nodeR:
                    nodeList.append(nodeL)
                else:
                    # if faces can't be joined on the fly, then add
                    # a new "line" and merge lines later
                    nodeList = [nodeL, nodeR]
                    self.patchFaceNodes[iPatch].append(nodeList)

        # sweep all faces and join lines together...
        if join:
            numberChanged = 100
            while numberChanged > 0:
                numberChanged = 0

                i = 0
                while i < len(plotLines):
                    deleteLines = []

                    for j in range(i+1, len(plotLines)):
                        if plotLines[i][-1] == plotLines[j][0]:
                            plotLines[i].extend(plotLines[j][1:])
                            deleteLines.append(j)
                        elif plotLines[i][-1] == plotLines[j][-1]:
                            plotLines[j].reverse()
                            plotLines[i].extend(plotLines[j][1:])
                            deleteLines.append(j)
                        elif plotLines[i][0] == plotLines[j][0]:
                            plotLines[i].reverse()
                            plotLines[i].extend(plotLines[j][1:])
                            deleteLines.append(j)
                        elif plotLines[i][0] == plotLines[j][-1]:
                            plotLines[i].reverse()
                            plotLines[j].reverse()
                            plotLines[i].extend(plotLines[j][1:])
                            deleteLines.append(j)

                    numberChanged += len(deleteLines)

                    for delLine in sorted(deleteLines, reverse=True):
                        del plotLines[delLine]

                    i += 1

            return plotLines

    def bladeRadius(self, bladePatches):
        self.geo.read()

        maxr = 0
        color = 'red'

        for iPatch in bladePatches:
            faces = np.where(self.geo.face2patch == iPatch)
            faces = faces[0]

            for iFace in faces:
                nodes = self.geo.faceNodes[iFace]
                Xplot = self.geo.x[nodes, 0:2]

                maxface = np.sqrt(np.sum([x**2 for x in Xplot]))

                if maxface > maxr:
                    maxr = maxface

                plt.plot(Xplot[:, 0], Xplot[:, 1], '-', c=color)

                plt.axis('equal')
