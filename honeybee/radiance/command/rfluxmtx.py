# coding=utf-8

from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceValue,RadianceNumber
from ..datatype import RadianceBoolFlag
from ..parameters.rfluxmtx import RfluxmtxParameters

import os



class Rfluxmtx(RadianceCommand):
    groundString = """
    void glow ground_glow
    0
    0
    4 1 1 1 0

    ground_glow source ground
    0
    0
    4 0 0 -1 180
    """

    skyString = """
    void glow sky_glow
    0
    0
    4 1 1 1 0

    sky_glow source sky
    0
    0
    4 0 0 1 180
    """

    class ControlParameters(object):
        def __init__(self, hemiType='u', hemiUpDirection='Y', outputFile=''):
            """Set the values for hemispheretype, hemisphere up direction
            and output file location(optional)."""
            self.hemisphereType = hemiType
            """
                The acceptable inputs for hemisphere type are:
                    u for uniform.(Usually applicable for ground).
                    kf for klems full.
                    kh for klems half.
                    kq for klems quarter.
                    rN for Reinhart - Tregenza type skies. N stands for subdivisions and defaults to 1.
                    scN for shirley-chiu subdivisions."""
            self.hemisphereUpDirection = hemiUpDirection
            """The acceptable inputs for hemisphere direction are %s""" % \
            (",".join(('X', 'Y', 'Z', 'x', 'y', 'z', '-X', '-Y',
                       '-Z', '-x', '-y', '-z')))
            self.outputFile = outputFile

        @property
        def hemisphereType(self):
            return self._hemisphereType

        @hemisphereType.setter
        def hemisphereType(self, value):
            """
                The acceptable inputs for hemisphere type are:
                    u for uniform.(Usually applicable for ground).\n
                    kf for klems full.\n
                    kh for klems half.\n
                    kq for klems quarter.\n
                    rN for Reinhart - Tregenza type skies. N stands for subdivisions and defaults to 1.\n
                    scN for shirley-chiu subdivisions."""
            if value:
                if value in ('u', 'kf', 'kh', 'kq'):
                    self._hemisphereType = value
                    return
                elif value.startswith('r'):
                    if len(value) > 1:
                        try:
                            num = int(value[1:])
                        except ValueError:
                            raise Exception(
                                "The format reinhart tregenza type skies is rN ."
                                "The value entered was %s" % value)
                    else:
                        num = ''
                    self._hemisphereType = 'r' + str(num)
                elif value.startswith('sc'):
                    if len(value) > 2:
                        try:
                            num = int(value[2:])
                        except ValueError:
                            raise Exception(
                                "The format for ShirleyChiu type values is scN."
                                "The value entered was %s" % value)
                    else:
                        raise Exception(
                            "The format for ShirleyChiu type values is scN."
                            "The value entered was %s" % value)
                    self._hemisphereType = 'sc' + str(num)
                else:
                    exceptStr = """
                    The acceptable inputs for hemisphere type are:
                        u for uniform.(Usually applicable for ground).
                        kf for klems full.
                        kh for klems half.
                        kq for klems quarter.
                        rN for Reinhart - Tregenza type skies. N stands for
                            subdivisions and defaults to 1.
                        scN for shirley-chiu subdivisions.
                    The value entered was %s
                    """ % (value)
                    raise Exception(exceptStr)

        @property
        def hemisphereUpDirection(self):
            return self._hemisphereUpDirection

        @hemisphereUpDirection.setter
        def hemisphereUpDirection(self, value):
            """The acceptable inputs for hemisphere direction are 'X', 'Y',
            'Z', 'x', 'y', 'z', '-X', '-Y','-Z', '-x', '-y','-z'"""
            if value:
                allowedValues = ('X', 'Y', 'Z', 'x', 'y', 'z', '-X', '-Y',
                                 '-Z', '-x', '-y', '-z',"+X","+Y","+Z",
                                 '+x',"+y","+z")
                assert value in allowedValues, "The value for hemisphereUpDirection" \
                                               "should be one of the following: %s" \
                                               % (','.join(allowedValues))

                self._hemisphereUpDirection = value

        def __str__(self):
            outputFileSpec = "o=%s" % self.outputFile if self.outputFile else ''
            return "#@rfluxmtx h=%s u=%s %s" % (self.hemisphereType,
                                                self.hemisphereUpDirection,
                                                outputFileSpec)

    @classmethod
    def defaultSkyGround(cls, fileName, skyType=None, skyFileFormat=None,
                         groundFileFormat=None):
        """

        Args:
            fileName:This should be the name of the file to which the sky defintion
                should be written to.

            skyType:The acceptable inputs for hemisphere type are:
                    u for uniform.(Usually applicable for ground).\n
                    kf for klems full.\n
                    kh for klems half.\n
                    kq for klems quarter.\n
                    rN for Reinhart - Tregenza type skies. N stands for
                        subdivisions and defaults to 1.\n
                    scN for shirley-chiu subdivisions.

        Returns:
            fileName: Passes back the same fileName that was provided as input.
        """

        skyParam = Rfluxmtx.ControlParameters(hemiType=skyType or 'r',
                                              outputFile=skyFileFormat)

        groundParam = Rfluxmtx.ControlParameters(hemiType='u',
                                                 outputFile=groundFileFormat)

        groundString = Rfluxmtx.addControlParameters(Rfluxmtx.groundString,
                                                     {'ground_glow': groundParam})
        skyString = Rfluxmtx.addControlParameters(Rfluxmtx.skyString,
                                                  {'sky_glow': skyParam})

        with open(fileName, 'w')as skyFile:
            skyFile.write(groundString + '\n' + skyString)

        return fileName

    @classmethod
    def addControlParameters(cls, inputString, modifierDict):
        if os.path.exists(inputString):
            with open(inputString)as fileString:
                fileData = fileString.read()
        else:
            fileData = inputString

        outputString = ''
        checkDict = dict.fromkeys(modifierDict.keys(), None)
        for lines in fileData.split('\n'):
            for key, value in modifierDict.items():
                if key in lines and not checkDict[
                    key] and not lines.strip().startswith('#'):
                    outputString += str(value) + '\n'
                    # outputString += lines.strip() + '\n'
                    checkDict[key] = True
            else:
                outputString += lines.strip() + '\n'

        for key, value in checkDict.items():
            assert value, "The modifier %s was not found in the string specified" % key

        if os.path.exists(inputString):
            newOutputFile = inputString + '_m'
            with open(newOutputFile, 'w')as newoutput:
                newoutput.write(outputString)
            outputString = newOutputFile
        return outputString

    @classmethod
    def checkForRfluxParameters(cls, fileVal):
        with open(fileVal)as rfluxFile:
            rfluxString = rfluxFile.read()
        assert '#@rfluxmtx' in rfluxString, \
            "The file %s does not have any rfluxmtx control parameters."
        return True

    # sender = RadiancePath('sender','sender file')
    receiverFile = RadiancePath('receiver', 'receiver file')
    octreeFile = RadiancePath('octree', 'octree file',extension='.oct')
    outputMatrix = RadiancePath('outputMatrix', 'output Matrix File')
    samplingRaysCount = RadianceNumber('c', 'number of sampling rays', numType=int)
    viewRaysFile = RadiancePath('viewRaysFile',
                                'file containing ray samples generated by vwrays')
    outputDataFormat = RadianceValue('f','output data format',isJoined=True)
    verbose = RadianceBoolFlag('v','verbose commands in stdout')
    numProcessors = RadianceNumber('n', 'number of processors',
                                    numType=int)
    def __init__(self, sender=None, receiverFile=None, octreeFile=None,
                 radFiles=None, pointsFile=None, outputMatrix=None,
                 viewRaysFile=None, viewInfoFile=None, outputFilenameFormat=None,
                 numProcessors=None):

        RadianceCommand.__init__(self)

        self.sender = sender
        """Sender file will be either a rad file containing rfluxmtx variables
         or just a - """

        self.receiverFile = receiverFile
        """Receiver file will usually be the sky file containing rfluxmtx
        variables"""

        self.octreeFile = octreeFile
        """Octree file containing the other rad file in the scene."""

        self.radFiles = radFiles
        """Rad files other than the sender and receiver that are a part of the
          scene."""

        self.pointsFile = pointsFile
        """The points file or input vwrays for which the illuminance/luminance
        value are to be calculated."""

        self.outputMatrix = outputMatrix
        """The flux matrix file that will be created by rfluxmtx."""

        self.pointsFileData = ''

        self.viewRaysFile= viewRaysFile
        """File containing ray samples generated from vwrays"""

        self.viewInfoFile = viewInfoFile
        """File containing view dimensions calculated from vwrays."""

        self.outputFilenameFormat = outputFilenameFormat
        """Filename format"""

        self.numProcessors = numProcessors
        """Number of processors"""

    @property
    def outputFilenameFormat(self):
        return self._outputFilenameFormat

    @outputFilenameFormat.setter
    def outputFilenameFormat(self,value):
        #TODO: Add testing logic for this !
        if value:
            self._outputFilenameFormat = value
        else:
            self._outputFilenameFormat = None

    @property
    def viewInfoFile(self):
        return self._viewInfoFile

    @viewInfoFile.setter
    def viewInfoFile(self,fileName):
        """
            The input for this setter is a file containing the view dimensions
            calculated through the -d option in rfluxmtx.
        """
        if fileName:
            assert os.path.exists(fileName),\
            "The file %s specified as viewInfoFile does not exist."
            self._viewInfoFile = fileName
            with open(fileName) as viewFileName:
                self._viewFileDimensions = viewFileName.read().strip()
        else:
            self._viewInfoFile = ''
            self._viewFileDimensions = ''

    @property
    def pointsFile(self):
        return self._pointsFile

    @pointsFile.setter
    def pointsFile(self, value):
        if value:
            if os.path.exists(value):
                with open(value)as pointsFile:
                    numberOfPoints = len(pointsFile.read().split())/6
                    self.pointsFileData += '-y %s' % numberOfPoints
                self._pointsFile = value
        else:
            self._pointsFile = ''
    @property
    def radFiles(self):
        """Get and set scene files."""
        return self.__radFiles

    @radFiles.setter
    def radFiles(self, files):
        if files:
            self.__radFiles = [os.path.normpath(f) for f in files]
        else:
            self.__radFiles = []

    @property
    def rfluxmtxParameters(self):
        return self.__rfluxmtxParameters

    @rfluxmtxParameters.setter
    def rfluxmtxParameters(self,parameters):
        self.__rfluxmtxParameters = parameters if parameters is not None\
            else RfluxmtxParameters()

        assert hasattr(self.rfluxmtxParameters, "isRadianceParameters"), \
            "input rfluxmtxParameters is not a valid parameters type."

    def toRadString(self, relativePath=False):
        octree = self.octreeFile.toRadString()
        octree = '-i %s'%self.normspace(octree) if octree else ''
        samplingCount = self.samplingRaysCount.toRadString()

        outputDataFormat = self.outputDataFormat.toRadString()
        verbose = self.verbose.toRadString()

        numberOfProcessors = self.numProcessors.toRadString()

        pointsFile = self.normspace(self.pointsFile)
        pointsFile = '< %s'%pointsFile if pointsFile else ''

        viewFileSamples = self.normspace(self.viewRaysFile.toRadString())
        viewFileSamples = '< %s'%viewFileSamples if viewFileSamples else ''

        assert not (pointsFile and viewFileSamples),\
        'View file and points file cannot be specified at the same time!'

        inputRays = pointsFile or viewFileSamples

        outputMatrix = self.normspace(self.outputMatrix.toRadString())
        outputMatrix = "> %s"%outputMatrix if outputMatrix else ''

        outputFilenameFormat = self.outputFilenameFormat
        outputFilenameFormat = "-o %s"%outputFilenameFormat if\
        outputFilenameFormat else ''
        #Lambda shortcut for adding an input or nothing to the command
        addToStr = lambda val: "%s "%val if val else ''

        #Creating the string this way because it might change again in the
        # future.
        radString = "%s "%self.normspace(os.path.join(self.radbinPath,
                                                     'rfluxmtx'))
        radString += addToStr(outputDataFormat)
        radString += addToStr(verbose)
        radString += addToStr(numberOfProcessors)
        radString += addToStr(self.pointsFileData)
        radString += addToStr(self._viewFileDimensions)
        radString += addToStr(samplingCount)
        radString += addToStr(self.rfluxmtxParameters.toRadString())
        radString += addToStr(outputFilenameFormat)
        radString += addToStr(self.sender)
        radString += addToStr(self.normspace(self.receiverFile.toRadString()))
        radString += addToStr(" ".join(self.radFiles))
        radString += addToStr(octree)
        radString += addToStr(inputRays)
        radString += addToStr(outputMatrix)

        return radString

    @property
    def inputFiles(self):
        return [self.receiverFile] + self.radFiles
