# -*- coding: utf-8 -*-
"""
Created on Tue May 30 11:44:38 2017

@author: m.dawson
"""

import numpy as np
import matplotlib.pyplot as plt


class IncompleteFile(EOFError):
    pass


class TorqueFile:
    def __init__(self, fileName, params=None, label=None):
        self.fileName = fileName
        self.label = label
        self.params = params
        self.readFile()
        self._afterFileReadHook()

    # File Reading Operations
    @staticmethod
    def readHeader(file):
        tmp = file.readline().rstrip('\n')
        tmp = tmp.split(',')

        nPatch = int(tmp[1])
        nTS = int(tmp[0])

        # discard header
        tmp = file.readline()

        return nPatch, nTS

    def readPatchNumbers(self):
        with open(self.fileName) as file:
            self.nPatch, self.nTS = self.readHeader(file)
            self.patches = np.empty([self.nPatch], dtype=int)

            for iPatch in range(0, self.nPatch):
                tmp = file.readline().split(',')

                self.patches[iPatch] = int(tmp[2])

    def readFile(self):

        try:
            with open(self.fileName) as file:
                self.readPatchNumbers()

                # explicitly set
                maxPatchIdx = np.max(self.patches) + 1

                self.nPatch, self.nTS = self.readHeader(file)

                self.time = np.empty(self.nTS, dtype=float)
                self.omega = np.empty(maxPatchIdx, dtype=float)

                self.torque = np.empty([self.nTS, maxPatchIdx], dtype=float)

                self.F = np.empty([self.nTS, maxPatchIdx, 3])

                self.X = np.empty([self.nTS, maxPatchIdx, 3])

                self.area = np.empty([self.nTS, maxPatchIdx])

                # read torque file
                lines = []
                for iTS in range(0, self.nTS):
                    for iPatch in range(0, self.nPatch):
                        line = file.readline()
                        lines.append(line)
                        tmp = line.split(',')

                        if len(tmp[0]) == 0 or len(tmp) < 11:
                            raise IncompleteFile('Torque file incomplete: %s' % self.fileName)

                        self.time[iTS] = float(tmp[0])
                        self.omega[iPatch] = float(tmp[1])

                        iPatchID = int(self.patches[iPatch])

                        if not iPatchID == float(tmp[2]):
                            raise ValueError('invalid file')

                        self.torque[iTS, iPatchID] = float(tmp[3])

                        self.F[iTS, iPatchID, 0] = float(tmp[4])
                        self.F[iTS, iPatchID, 1] = float(tmp[5])
                        self.F[iTS, iPatchID, 2] = float(tmp[6])

                        self.X[iTS, iPatchID, 0] = float(tmp[7])
                        self.X[iTS, iPatchID, 1] = float(tmp[8])
                        self.X[iTS, iPatchID, 2] = float(tmp[9])

                        self.area[iTS, iPatchID] = float(tmp[10])
                fileSuccess = True
        except IncompleteFile as incompleteFileException:
            # remove last (possibly incomplete) timestep
            print(incompleteFileException.message)
            iTS = iTS - 1
            self.truncateTorqueFile(iTS)
            fileSuccess = False

        return fileSuccess

    def _afterFileReadHook(self):
        self.timesteps = np.array([i + 1 for i in range(0, self.nTS)])

    def truncateTorqueFile(self, nTS):
        self.time = self.time[1:nTS]

        self.torque = self.torque[1:nTS, :]

        self.F = self.F[1:nTS, :, :]

        self.X = self.X[1:nTS, :, :]

        # adjust for zero indexing
        self.nTS = nTS - 1

    # Attribute accessors

    def num_revs(self):
        return self.X.shape[0] / self.params.StepsPerRev

    def T(self):
        return np.max(self.time)

    # Computed Attribute Accessors
    def getTotalTorquePerTimeStep(self, patches=None):
        if patches is None:
            patches = self.patches

        totTorque = np.zeros(self.nTS)

        for iTS in range(0, self.nTS):
            for iPatch in patches:
                totTorque[iTS] = totTorque[iTS] + self.torque[iTS, iPatch]

        return totTorque

    def getGivenRevStartTS(self, iRev):
        if (iRev < 1):
            raise ValueError('input revolution value should be larger than 1')
        return (iRev - 1) * self.params.StepsPerRev

    def getMeanCpOverLastNRevs(self, nRev, plot=False, xunits='revs'):
        iRev = self.getNRevs() - nRev + 1
        meancp, tStepStart, tStepEnd, lines = self.getMeanCpOverRevs(iRev, nRev, plot=plot, xunits=xunits)

        return meancp, tStepStart, tStepEnd, lines

    def getMeanCpOverRevs(self, iRev, nRev, xunits='revs', plot=False):
        meanTorque, tStepStart, tStepEnd = self.getMeanTorqueOverRevs(iRev, nRev)
        simpower = self._calcSimulatedPower(meanTorque)
        thpower = self.getTheoreticalPower()

        meancp = (simpower / thpower) * 100

        if (plot):
            l = self._plotScalarOverRange(meancp, tStepStart, tStepEnd, xunits=xunits)
        else:
            l = []

        return meancp, tStepStart, tStepEnd, l

    def getNRevs(self):
        return self.nTS / self.params.StepsPerRev

    # Drawing/Plotting Methods
    def drawTorqueVector(self, iStep, iPatch, scalefactor=3000, linestyle='-', color=False):
        Xstart = self.X[iStep, iPatch, :2]
        F = self.F[iStep, iPatch, :2]
        Funit = F / np.sqrt(np.sum(F ** 2))
        T = self.torque[iStep, iPatch]
        Ftorque = Funit * (np.abs(T) / scalefactor)
        Xend = Xstart + Ftorque

        plt.arrow(Xstart[0], Xstart[1], Xend[0] - Xstart[0], Xend[1] - Xstart[1], head_width=0.1, head_length=0.2,
                  fc=color, ec=color, linestyle=linestyle, linewidth=1)

        return T

    def plotTransientTorque(self, xunits='revs', color='red'):
        totalTorquePerTimeStep = self.getTotalTorquePerTimeStep()

        return self._plotTransientOverRange(totalTorquePerTimeStep, xunits=xunits, ylabel='torque', color=color)

    def _plotTransientOverRange(self, transient, tSteps=None, xunits='revs', color=None):

        if tSteps is None:
            tSteps = self.timesteps

        if xunits == 'time':
            time = [self.time[i] for i in tSteps - 1]
        elif xunits == 'revs':
            time = np.true_divide(tSteps, self.params.StepsPerRev)
        elif xunits == 'timesteps':
            time = tSteps
        else:
            raise ValueError('%s not valid xunits value' % xunits)

        if color is None:
            l, = plt.plot(time, transient, label=self.label)
        else:
            l, = plt.plot(time, transient, label=self.label, color=color)

        return time, transient, l

    def _plotScalarOverRange(self, scalar, tStepStart, tStepEnd, xunits='revs'):
        tSteps = np.array([tStepStart, tStepEnd], dtype=int)

        if xunits == 'time':
            time = [self.time[tStepStart - 1], self.time[tStepEnd - 1]]
            xlabel = 'time'
        elif xunits == 'revs':
            time = np.true_divide(tSteps, self.params.StepsPerRev)
            xlabel = 'window end time (revolutions)'
        elif xunits == 'timesteps':
            time = tSteps
            xlabel = 'timesteps'
        else:
            raise ValueError('%s not valid xunits value' % xunits)

        l, = plt.plot(time, [scalar, scalar])

        plt.xlabel(xlabel)

        return l, time

    def getMeanTorqueOverRevs(self, iRev, nRev, plot=False, xunits='revs'):
        totalTorquePerTimeStep = self.getTotalTorquePerTimeStep()

        endRev = int(self.getGivenRevStartTS(iRev + nRev))
        startRev = endRev - self.params.StepsPerRev * nRev

        if (endRev > self.nTS):
            raise ValueError('revolution %d is outside of range' % (iRev + nRev))

        timesteps = self.timesteps[startRev:endRev]
        totalTorquePerTimeStep = totalTorquePerTimeStep[startRev:endRev]

        meanTorque = np.mean(totalTorquePerTimeStep)

        if plot:
            self._plotTransientOverRange(totalTorquePerTimeStep, tSteps=timesteps, xunits=xunits)
            self._plotScalarOverRange(meanTorque, startRev, endRev, xunits=xunits)

        return meanTorque, startRev, endRev

    def plotTransientTorqueGivenRev(self, iRev, xunits='revs', labeloff=False):
        totalTorquePerTimeStep = self.getTotalTorquePerTimeStep()

        tSteps = np.array([i + 1 for i in range(0, self.nTS)])

        startRev = self.getGivenRevStartTS(iRev)
        endRev = self.getGivenRevStartTS(iRev + 1)

        totalTorquePerTimeStep = totalTorquePerTimeStep[startRev:endRev]
        tSteps = tSteps[startRev:endRev]
        tSteps = tSteps - tSteps[0]

        if xunits == 'time':
            time = self.time[startRev:endRev]
            xlabel = 'time'
        elif xunits == 'revs':
            time = tSteps / self.params.StepsPerRev
            xlabel = 'window end time (revolutions)'
        elif xunits == 'timesteps':
            time = tSteps
            xlabel = 'timesteps'
        else:
            raise ValueError('%s not valid xunits value' % xunits)

        if labeloff:
            label = None
        else:
            label = self.label

        l, = plt.plot(time, totalTorquePerTimeStep, label=label)

        plt.ylim([0, np.max(totalTorquePerTimeStep) * 1.1])

        plt.xlabel(xlabel)
        plt.ylabel('torque')

        return (time, totalTorquePerTimeStep, l)

    def _calcSimulatedPower(self, torque):
        return torque * (self.params.TSR * self.params.Uinf / self.params.R)

    # Power and Torque per Time Step

    def getSimulatedPowerPerTimeStep(self):
        return self._calcSimulatedPower(self.getTotalTorquePerTimeStep())

    def getTheoreticalPower(self):
        return 0.5 * self.params.density * (self.params.R * 2) * self.params.Uinf ** 3

    def getCpPerTimeStep(self):
        return 100 * self.getSimulatedPowerPerTimeStep() / self.getTheoreticalPower()

    def getDt(self):
        return self.time[-1] - self.time[-2]

    # Power and Torque per Revolution
    def getMeanTorqueSlidingWindow(self, n_revs_window=1, patches=None):
        if patches is None:
            patches = self.patches

        totalTorquePerTimeStep = self.getTotalTorquePerTimeStep(patches=patches)

        nSteps = np.round(n_revs_window * self.params.StepsPerRev)
        meanTorquePrevRev = [np.mean(totalTorquePerTimeStep[iTS:iTS + nSteps]) for iTS in range(0, self.nTS - nSteps)]
        meanTorquePrevRev = np.array(meanTorquePrevRev)
        tStepsEndRev = np.array([iTS + nSteps for iTS in range(0, self.nTS - nSteps)])

        return (meanTorquePrevRev, tStepsEndRev)

    def getTransientCpSlidingWindow(self, n_revs_window=1, plot=False, patches=None):
        if patches is None:
            patches = self.patches
        torque, tSteps = self.getMeanTorqueSlidingWindow(n_revs_window=n_revs_window, patches=patches)
        cp = 100 * self._calcSimulatedPower(torque) / self.getTheoreticalPower()

        if plot:
            time, transient, l = self._plotTransientOverRange(cp, tSteps=tSteps, xunits='revs', ylabel='Cp')
        else:
            l = None

        return (cp, tSteps, l)

    def plotTransientCp(self, xunits='revs'):
        CpPerTimeStep = self.getCpPerTimeStep()

        return self._plotTransientOverRange(CpPerTimeStep, xunits=xunits, ylabel='Cp')

    def set_label(self, label):
        self.label = label

        if len(self.l) > 0:
            plt.setp(self.l, 'label', self.label)


class ResumedTorqueFile(TorqueFile):
    def __init__(self, fileNames, params=None, label=None):
        super(ResumedTorqueFile, self).__init__(fileNames, params=None, label=None)
        self.fileName = fileNames[1]
        self.label = label
        self.params = params
        self.readFile()

        time = self.time
        omega = self.omega
        torque = self.torque
        F = self.F
        X = self.X
        area = self.area

        self.fileName = fileNames[0]

        self.readFile()

        self.time = np.append(self.time, time)
        self.omega = np.append(self.omega, omega)

        self.torque = np.append(self.torque, torque, axis=0)

        self.F = np.append(self.F, F, axis=0)

        self.X = np.append(self.X, X, axis=0)

        self.area = np.append(self.area, area, axis=0)

        self.patches = self.patches

        self.nTS = len(self.time)

        self._afterFileReadHook()
