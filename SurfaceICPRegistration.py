import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# SurfaceICPRegistration
#

class SurfaceICPRegistration:
  def __init__(self, parent):
    parent.title = "Surface ICP Registration"
    parent.categories = ["Registration"]
    parent.dependencies = []
    parent.contributors = ["Vinicius Boen(Univ of Michigan)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Help text.
    """
    parent.acknowledgementText = """
    Acknowledgemen text
    """ # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['SurfaceICPRegistration'] = self.runTest

  def runTest(self):
    tester = SurfaceICPRegistration()
    tester.runTest()

#
# qSurfaceICPRegistrationWidget
#
class SurfaceICPRegistrationWidget:
  """The module GUI widget"""
  def __init__(self, parent = None):
    self.logic = SurfaceICPRegistrationLogic()
    self.sliceNodesByViewName = {}
    self.sliceNodesByVolumeID = {}
    self.observerTags = []

    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    """Instantiate and connect widgets ..."""

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "SurfaceICPRegistration Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Input/Output Surface Volume Collapsible Button
    #
    IOSurfaceCollapsibleButton = ctk.ctkCollapsibleButton()
    IOSurfaceCollapsibleButton.text = "Input/Output Surface Volumes"
    self.layout.addWidget(IOSurfaceCollapsibleButton)
    IOSurfaceFormLayout = qt.QFormLayout(IOSurfaceCollapsibleButton)
    
	#
	# Input/Output Surface Volume Options
	#
    self.volumeSelectors = {}
    self.viewNames = ("Fixed Surface Volume", "Moving Surface Volume", "Output Surface Volume", "initial Transform")
    for viewName in self.viewNames:
      self.volumeSelectors[viewName] = slicer.qMRMLNodeComboBox()
      self.volumeSelectors[viewName].nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
      self.volumeSelectors[viewName].selectNodeUponCreation = False
      self.volumeSelectors[viewName].addEnabled = False
      self.volumeSelectors[viewName].removeEnabled = True
      self.volumeSelectors[viewName].noneEnabled = True
      self.volumeSelectors[viewName].showHidden = False
      self.volumeSelectors[viewName].showChildNodeTypes = True
      self.volumeSelectors[viewName].setMRMLScene( slicer.mrmlScene )
      self.volumeSelectors[viewName].setToolTip( "Pick the %s surface volume." % viewName.lower() )
      IOSurfaceFormLayout.addRow("%s" % viewName, self.volumeSelectors[viewName])
    
    self.volumeSelectors["Output Surface Volume"].addEnabled = True
    self.volumeSelectors["Output Surface Volume"].selectNodeUponCreation = True
	
    self.volumeSelectors["initial Transform"].addEnabled = True
    self.volumeSelectors["initial Transform"].selectNodeUponCreation = True
    self.volumeSelectors["initial Transform"].setToolTip( "Pick the initial Transform file" )
	
    #
    # Input Registration Parameters Collapsible Button
    #
    inputRegistrationParametersCollapsibleButton = ctk.ctkCollapsibleButton()
    inputRegistrationParametersCollapsibleButton.text = "Input Registration Parameters"
    self.layout.addWidget(inputRegistrationParametersCollapsibleButton)
    inputRegistrationParametersFormLayout = qt.QFormLayout(inputRegistrationParametersCollapsibleButton)
	
    #
    # Landmark Transform Mode TYPE SELECTION
    # - allows selection of the active registration type to display
    #
    self.landmarkTransformTypeBox = qt.QGroupBox("Landmark Transform Mode")
    self.landmarkTransformTypeBox.setLayout(qt.QFormLayout())
    self.landmarkTransformTypeButtons = {}
    self.landmarkTransformTypes = ("Rigid", "Similarity", "Affine")
    for landmarkTransformType in self.landmarkTransformTypes:
      self.landmarkTransformTypeButtons[landmarkTransformType] = qt.QRadioButton()
      self.landmarkTransformTypeButtons[landmarkTransformType].text = landmarkTransformType
      self.landmarkTransformTypeButtons[landmarkTransformType].setToolTip("Pick the type of registration")
      self.landmarkTransformTypeButtons[landmarkTransformType].connect("clicked()",
                                      lambda t=landmarkTransformType: self.onLandmarkTrandformType(t))
      self.landmarkTransformTypeBox.layout().addWidget(self.landmarkTransformTypeButtons[landmarkTransformType])
    inputRegistrationParametersFormLayout.addWidget(self.landmarkTransformTypeBox)

	#
	# Mean Distance Mode TYPE SELECTION
	#
    self.meanDistanceTypeBox2 = qt.QGroupBox("Mean Distance Mode")
    self.meanDistanceTypeBox2.setLayout(qt.QFormLayout())
    self.meanDistanceTypeButtons2 = {}
    self.meanDistanceTypes2 = ("RMS", "Absolute Value")
    inputRegistrationParametersFormLayout.addWidget(self.landmarkTransformTypeBox)
    for meanDistanceType2 in self.meanDistanceTypes2:
      self.meanDistanceTypeButtons2[meanDistanceType2] = qt.QRadioButton()
      self.meanDistanceTypeButtons2[meanDistanceType2].text = meanDistanceType2
      self.meanDistanceTypeButtons2[meanDistanceType2].setToolTip("Pick the type of registration")
      self.meanDistanceTypeButtons2[meanDistanceType2].connect("clicked()",
                                      lambda t=meanDistanceType2: self.onMeanDistanceType(t))
      self.meanDistanceTypeBox2.layout().addWidget(self.meanDistanceTypeButtons2[meanDistanceType2])
    inputRegistrationParametersFormLayout.addWidget(self.meanDistanceTypeBox2)
    
    #
	# Start by Matching Centroids Options
	#
    self.startMatchingCentroids = qt.QCheckBox()
    self.startMatchingCentroids.checked = True
    self.startMatchingCentroids.connect("toggled(bool)", self.onMatchCentroidsLinearActive)
    inputRegistrationParametersFormLayout.addRow("Start by matching centroids ", self.startMatchingCentroids)
	
	#
	# Check Mean Distance Options
	#
    self.checkMeanDistance = qt.QCheckBox()
    self.checkMeanDistance.checked = True
    self.checkMeanDistance.connect("toggled(bool)", self.onCheckMeanDistanceActive)
    inputRegistrationParametersFormLayout.addRow("Check Mean Distance ", self.checkMeanDistance)	
	
    # Number of Iterations
    numberOfIterations = ctk.ctkSliderWidget()
    numberOfIterations.connect('valueChanged(double)', self.numberOfIterationsValueChanged)
    numberOfIterations.decimals = 0
    numberOfIterations.minimum = 50
    numberOfIterations.maximum = 80000
    numberOfIterations.value = 50
    inputRegistrationParametersFormLayout.addRow("Number of Iterations:", numberOfIterations)
    
	# Number of Landmarks
    numberOfLandmarks = ctk.ctkSliderWidget()
    numberOfLandmarks.connect('valueChanged(double)', self.numberOfLandmarksValueChanged)
    numberOfLandmarks.decimals = 0
    numberOfLandmarks.minimum = 0
    numberOfLandmarks.maximum = 10000
    numberOfLandmarks.value = 200
    inputRegistrationParametersFormLayout.addRow("Number of Landmarks:", numberOfLandmarks)
	
	# Maximum Distance
    maxDistance = ctk.ctkSliderWidget()
    maxDistance.connect('valueChanged(double)', self.maxDistanceValueChanged)
    maxDistance.decimals = 4
    maxDistance.minimum = 0.0001
    maxDistance.maximum = 10
    maxDistance.value = 0.01
    inputRegistrationParametersFormLayout.addRow("Maximum Distance:", maxDistance)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Run Registration")
    self.applyButton.toolTip = "Run the registration algorithm."
    self.applyButton.enabled = True
    inputRegistrationParametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    for selector in self.volumeSelectors.values():
      selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onVolumeNodeSelect)

    # listen to the scene
    self.addObservers()

    # Add vertical spacer
    self.layout.addStretch(1)

  def numberOfIterationsValueChanged(self, newValue):
    #print "frameSkipSliderValueChanged:", newValue
    self.skip = int(newValue)

  def maxDistanceValueChanged(self, newValue):
    #print "frameSkipSliderValueChanged:", newValue
    self.skip = int(newValue)

  def numberOfLandmarksValueChanged(self, newValue):
    #print "frameSkipSliderValueChanged:", newValue
    self.skip = int(newValue)
	
  def cleanup(self):
    self.removeObservers()

  def addObservers(self):
    """Observe the mrml scene for changes that we wish to respond to.
    scene observer:
     - whenever a new node is added, check if it was a new fiducial.
       if so, transform it into a landmark by putting it in the correct
       hierarchy and creating a matching fiducial for other voluemes
    fiducial obserers:
     - when fiducials are manipulated, perform (or schedule) an update
       to the currently active registration method.
    """
    #tag = slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAddedEvent, self.landmarksWidget.requestNodeAddedUpdate)
    #self.observerTags.append( (slicer.mrmlScene, tag) )

  def removeObservers(self):
    """Remove observers and any other cleanup needed to
    disconnect from the scene"""
    #for obj,tag in self.observerTags:
    #  obj.RemoveObserver(tag)
    #self.observerTags = []

  def currentVolumeNodes(self):
    """List of currently selected volume nodes"""
    volumeNodes = []
    for selector in self.volumeSelectors.values():
      volumeNode = selector.currentNode()
      if volumeNode:
        volumeNodes.append(volumeNode)
    return(volumeNodes)

  def onVolumeNodeSelect(self):
    """When one of the volume selectors is changed"""
    #volumeNodes = self.currentVolumeNodes()
    #self.landmarksWidget.setVolumeNodes(volumeNodes)
    #fixed = self.volumeSelectors['Fixed'].currentNode()
    #moving = self.volumeSelectors['Moving'].currentNode()
    #transformed = self.volumeSelectors['Transformed'].currentNode()
    #for registrationType in self.registrationTypes:
    #  self.registrationTypeInterfaces[registrationType].enabled = bool(fixed and moving)
    #self.logic.hiddenFiducialVolumes = (transformed,)

  #def onLayout(self, layoutMode="Axi/Sag/Cor",volumesToShow=None):
  #  """When the layout is changed by the VisualizationWidget
  #  volumesToShow: list of the volumes to include, None means include all
  #  """
  #  volumeNodes = []
  #  activeViewNames = []
  #  for viewName in self.viewNames:
  #    volumeNode = self.volumeSelectors[viewName].currentNode()
  #    if volumeNode and not (volumesToShow and viewName not in volumesToShow):
  #      volumeNodes.append(volumeNode)
  #      activeViewNames.append(viewName)
  #  import CompareVolumes
  #  compareLogic = CompareVolumes.CompareVolumesLogic()
  #  oneViewModes = ('Axial', 'Sagittal', 'Coronal',)
  #  if layoutMode in oneViewModes:
  #    self.sliceNodesByViewName = compareLogic.viewerPerVolume(volumeNodes,viewNames=activeViewNames,orientation=layoutMode)
  #  elif layoutMode == 'Axi/Sag/Cor':
  #    self.sliceNodesByViewName = compareLogic.viewersPerVolume(volumeNodes)
  #  self.overlayFixedOnTransformed()
  #  self.updateSliceNodesByVolumeID()
  #  self.onLandmarkPicked(self.landmarksWidget.selectedLandmark)

  #def overlayFixedOnTransformed(self):
  #  """If there are viewers showing the tranfsformed volume
  #  in the background, make the foreground volume be the fixed volume
  #  and set opacity to 0.5"""
  #  fixedNode = self.volumeSelectors['Fixed'].currentNode()
  #  transformedNode = self.volumeSelectors['Transformed'].currentNode()
  #  if transformedNode:
  #    compositeNodes = slicer.util.getNodes('vtkMRMLSliceCompositeNode*')
  #    for compositeNode in compositeNodes.values():
  #      if compositeNode.GetBackgroundVolumeID() == transformedNode.GetID():
  #        compositeNode.SetForegroundVolumeID(fixedNode.GetID())
  #        compositeNode.SetForegroundOpacity(0.5)

  def onLandmarkTrandformType(self,pickedRegistrationType):
    """Pick which landmark transform"""
    #for registrationType in self.registrationTypes:
    #  self.registrationTypeInterfaces[registrationType].hide()
    #self.registrationTypeInterfaces[pickedRegistrationType].show()

  def onMeanDistanceType(self,pickedRegistrationType):
	    """Pick which distance mode"""
    #for registrationType in self.registrationTypes:
    #  self.registrationTypeInterfaces[registrationType].hide()
    #self.registrationTypeInterfaces[pickedRegistrationType].show()
	
	
  def onMatchCentroidsLinearActive(self,active):
    """initialize the transform by translating the input surface so 
	that its centroid coincides the centroid of the target surface."""
    #if not active:
    #  print('skipping registration')
    #  self.logic.disableLinearRegistration()
    #else:
    #  # ensure we have fixed and moving
    #  fixed = self.volumeSelectors['Fixed'].currentNode()
    #  moving = self.volumeSelectors['Moving'].currentNode()
    #  if not (fixed and moving):
    #    self.linearRegistrationActive.checked = False
    #  else:
    #    # create transform and transformed if needed
    #    transform = self.linearTransformSelector.currentNode()
    #    if not transform:
    #      self.linearTransformSelector.addNode()
    #      transform = self.linearTransformSelector.currentNode()
    #    transformed = self.volumeSelectors['Transformed'].currentNode()
    #    if not transformed:
    #      volumesLogic = slicer.modules.volumes.logic()
    #      transformedName = "%s-transformed" % moving.GetName()
    #      transformed = volumesLogic.CloneVolume(slicer.mrmlScene, moving, transformedName)
    #      self.volumeSelectors['Transformed'].setCurrentNode(transformed)
    #    landmarks = self.logic.landmarksForVolumes((fixed,moving))
    #    self.logic.enableLinearRegistration(fixed,moving,landmarks,transform,transformed)

  def onCheckMeanDistanceActive(self,active):
    """ force checking distance between every two iterations (slower but more accurate)"""
    #if not active:
    #  print('skipping registration')
    #  self.logic.disableLinearRegistration()
    #else:
    #  # ensure we have fixed and moving
    #  fixed = self.volumeSelectors['Fixed'].currentNode()
    #  moving = self.volumeSelectors['Moving'].currentNode()
    #  if not (fixed and moving):
    #    self.linearRegistrationActive.checked = False
    #  else:
    #    # create transform and transformed if needed
    #    transform = self.linearTransformSelector.currentNode()
    #    if not transform:
    #      self.linearTransformSelector.addNode()
    #      transform = self.linearTransformSelector.currentNode()
    #    transformed = self.volumeSelectors['Transformed'].currentNode()
    #    if not transformed:
    #      volumesLogic = slicer.modules.volumes.logic()
    #      transformedName = "%s-transformed" % moving.GetName()
    #      transformed = volumesLogic.CloneVolume(slicer.mrmlScene, moving, transformedName)
    #      self.volumeSelectors['Transformed'].setCurrentNode(transformed)
    #    landmarks = self.logic.landmarksForVolumes((fixed,moving))
    #    self.logic.enableLinearRegistration(fixed,moving,landmarks,transform,transformed)

  #def onLinearTransform(self):
  #  """Call this whenever linear transform needs to be updated"""
  #  for mode in self.linearModes:
  #    if self.linearModeButtons[mode].checked:
  #      self.logic.linearMode = mode
  #      self.onLinearActive(self.linearRegistrationActive.checked)
  #      break

  #def onThinPlateApply(self):
  #  """Call this whenever thin plate needs to be calculated"""
  #  fixed = self.volumeSelectors['Fixed'].currentNode()
  #  moving = self.volumeSelectors['Moving'].currentNode()
  #  if fixed and moving:
  #    transformed = self.volumeSelectors['Transformed'].currentNode()
  #    if not transformed:
  #      volumesLogic = slicer.modules.volumes.logic()
  #      transformedName = "%s-transformed" % moving.GetName()
  #      transformed = volumesLogic.CloneVolume(slicer.mrmlScene, moving, transformedName)
  #      self.volumeSelectors['Transformed'].setCurrentNode(transformed)
  #    landmarks = self.logic.landmarksForVolumes((fixed,moving))
  #    self.logic.performThinPlateRegistration(fixed,moving,landmarks,transformed)

  #def onHybridTransformApply(self):
  #  """Call this whenever hybrid transform needs to be calculated"""
  #  import os,sys
  #  loadablePath = os.path.join(slicer.modules.plastimatch_slicer_bspline.path,'../../qt-loadable-modules')
  #  if loadablePath not in sys.path:
  #    sys.path.append(loadablePath)
  #  import vtkSlicerPlastimatchModuleLogicPython
  #  print('running...')

  #def updateSliceNodesByVolumeID(self):
  #  """Build a mapping to a list of slice nodes
  #  node that are currently displaying a given volumeID"""
  #  compositeNodes = slicer.util.getNodes('vtkMRMLSliceCompositeNode*')
  #  self.sliceNodesByVolumeID = {}
  #  if self.sliceNodesByViewName:
  #    for sliceNode in self.sliceNodesByViewName.values():
  #      for compositeNode in compositeNodes.values():
  #        if compositeNode.GetLayoutName() == sliceNode.GetLayoutName():
  #          volumeID = compositeNode.GetBackgroundVolumeID()
  #          if self.sliceNodesByVolumeID.has_key(volumeID):
  #            self.sliceNodesByVolumeID[volumeID].append(sliceNode)
  #          else:
  #            self.sliceNodesByVolumeID[volumeID] = [sliceNode,]

  #def restrictLandmarksToViews(self):
  #  """Set fiducials so they only show up in the view
  #  for the volume on which they were defined"""
  #  volumeNodes = self.currentVolumeNodes()
  #  if self.sliceNodesByViewName:
  #    landmarks = self.logic.landmarksForVolumes(volumeNodes)
  #    for fidList in landmarks.values():
  #      for fid in fidList:
  #        displayNode = fid.GetDisplayNode()
  #        displayNode.RemoveAllViewNodeIDs()
  #        volumeNodeID = fid.GetAttribute("AssociatedNodeID")
  #        if volumeNodeID:
  #          if self.sliceNodesByVolumeID.has_key(volumeNodeID):
  #            for sliceNode in self.sliceNodesByVolumeID[volumeNodeID]:
  #              displayNode.AddViewNodeID(sliceNode.GetID())

  #def onLandmarkPicked(self,landmarkName):
  #  """Jump all slice views such that the selected landmark
  #  is visible"""
  #  if not self.landmarksWidget.movingView:
  #    # only change the fiducials if they are not being manipulated
  #    self.restrictLandmarksToViews()
  #  self.updateSliceNodesByVolumeID()
  #  volumeNodes = self.currentVolumeNodes()
  #  fiducialsByName = self.logic.landmarksForVolumes(volumeNodes)
  #  if fiducialsByName.has_key(landmarkName):
  #    landmarksFiducials = fiducialsByName[landmarkName]
  #    for fid in landmarksFiducials:
  #      volumeNodeID = fid.GetAttribute("AssociatedNodeID")
  #      if self.sliceNodesByVolumeID.has_key(volumeNodeID):
  #        point = [0,]*3
  #        fid.GetFiducialCoordinates(point)
  #        for sliceNode in self.sliceNodesByVolumeID[volumeNodeID]:
  #          if sliceNode.GetLayoutName() != self.landmarksWidget.movingView:
  #            sliceNode.JumpSliceByCentering(*point)

  #def onLandmarkMoved(self,landmarkName):
  #  """Called when a landmark is moved (probably through
  #  manipulation of the widget in the slice view).
  #  This updates the active registration"""
  #  if self.linearRegistrationActive.checked and not self.landmarksWidget.movingView:
  #    self.onLinearActive(True)

  def onApplyButton(self):
    print("Run the algorithm")
    #self.logic.run(self.fixedSelector.currentNode(), self.movingSelector.currentNode())

  def onReload(self,moduleName="SurfaceICPRegistration"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])

  def onReloadAndTest(self,moduleName="SurfaceICPRegistration",scenario=None):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest(scenario=scenario)
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")

		  
		  
		  
class pqWidget(object):
  """
  A "QWidget"-like widget class that manages provides some
  helper functionality (signals, slots...)
  """
  def __init__(self):
    self.connections = {} # list of slots per signal

  def connect(self,signal,slot):
    """pseudo-connect - signal is arbitrary string and slot if callable"""
    if not self.connections.has_key(signal):
      self.connections[signal] = []
    self.connections[signal].append(slot)

  def disconnect(self,signal,slot):
    """pseudo-disconnect - remove the connection if it exists"""
    if self.connections.has_key(signal):
      if slot in self.connections[signal]:
        self.connections[signal].remove(slot)

  def emit(self,signal,args):
    """pseudo-emit - calls any slots connected to signal"""
    if self.connections.has_key(signal):
      for slot in self.connections[signal]:
        slot(*args)

class LandmarksWidget(pqWidget):
  """ A "QWidget"-like class that manages a set of landmarks that are pairs of fiducials """

  def __init__(self,logic):
    super(LandmarksWidget,self).__init__()
    self.logic = logic
    self.volumeNodes = []
    self.buttons = {} # the current buttons in the group box

    self.widget = qt.QWidget()

	
#
# SurfaceICPRegistrationLogic
#
class SurfaceICPRegistrationLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    self.linearMode = 'Rigid'
    self.hiddenFiducialVolumes = ()

  def run(self,inputVolume,outputVolume):
    "Run the actual algorithm"
    return True