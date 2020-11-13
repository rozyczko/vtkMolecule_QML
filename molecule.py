__author__ = 'github.com/rozyczko'
__version__ = '0.0.1'

from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, Signal, Property, Slot, Qt
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlEngine
from PySide2.QtWidgets import QApplication
import PySide2.QtGui as QtGui

import numpy as np

from Mixed.QVTKFrameBufferObjectItem import FboItem

import sys


def defaultFormat(stereo_capable):
    """
    Copied from https://github.com/Kitware/VTK/blob/master/GUISupport/Qt/QVTKRenderWindowAdapter.cxx
    """
    fmt = QtGui.QSurfaceFormat()
    fmt.setRenderableType(QtGui.QSurfaceFormat.OpenGL)
    fmt.setVersion(3, 2)
    fmt.setProfile(QtGui.QSurfaceFormat.CoreProfile)
    fmt.setSwapBehavior(QtGui.QSurfaceFormat.DoubleBuffer)
    fmt.setRedBufferSize(8)
    fmt.setGreenBufferSize(8)
    fmt.setBlueBufferSize(8)
    fmt.setDepthBufferSize(8)
    fmt.setAlphaBufferSize(8)
    fmt.setStencilBufferSize(0)
    fmt.setStereo(stereo_capable)
    fmt.setSamples(0)

    return fmt


class App(QApplication):

    def __init__(self, sys_argv):
        # sys_argv += ["-style", "material"]  #! MUST HAVE
        self._m_vtkFboItem = None
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
        QtGui.QSurfaceFormat.setDefaultFormat(defaultFormat(False))  # from vtk 8.2.0
        super(App, self).__init__(sys_argv)

    def startApplication(self):
        qDebug('CanvasHandler::startApplication()')
        self._m_vtkFboItem.rendererInitialized.disconnect(self.startApplication)

    def setup(self, engine):
        # Get reference to the QVTKFramebufferObjectItem in QML
        rootObject = engine.rootObjects()[0]  # returns QObject
        self._m_vtkFboItem = rootObject.findChild(FboItem, 'vtkFboItem')

        # Give the vtkFboItem reference to the CanvasHandler
        if (self._m_vtkFboItem):
            qDebug('CanvasHandler::CanvasHandler: setting vtkFboItem to CanvasHandler')
            self._m_vtkFboItem.rendererInitialized.connect(self.startApplication)
        else:
            qCritical('CanvasHandler::CanvasHandler: Unable to get vtkFboItem instance')
            return


class canvasHandler(QObject):

    def __init__(self, parent=None):
        super(canvasHandler, self).__init__(parent=parent)
        self.fbo = None
        self.actors = []

    @Slot(str)
    def openModel(self, fileName):
        print(f'Otwieram: {fileName}')
        self.fbo.addModel(fileName)

    @Slot()
    def clearScene(self):
        for actor in self.actors:
            self.fbo.removeActor(actor, update=False)
        self.actors = []
        self.fbo.update()

    @Slot()
    def create_structure(self):
        import vtk  # REQUIRES VTK < 9.0!!!
        # molecule
        mol = vtk.vtkMolecule()

        # hardcoded structure CO2
        a1 = mol.AppendAtom(6, 0.0, 0.0, 0.0)
        a2 = mol.AppendAtom(8, 0.0, 0.0, -1.0)
        a3 = mol.AppendAtom(8, 0.0, 0.0, 1.0)
        mol.AppendBond(a2, a1, 1)
        mol.AppendBond(a3, a1, 1)

        # hardcoded cell, cubic 10x10x10
        vector = vtk.vtkMatrix3x3()
        vector.DeepCopy([10, 0, 0,
                        0, 10, 0,
                        0, 0, 10])
        mol.SetLattice(vector)

        # Change lattice origin so molecule is in the centre
        mol.SetLatticeOrigin(vtk.vtkVector3d(-5.0, -5.0, -5.0))

        # Create a mapper and actor
        mapper = vtk.vtkMoleculeMapper()
        mapper.SetInputData(mol)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.fbo.addActors([actor])

        self.fbo.update()

    @Slot(int, int, int)
    def mousePressEvent(self, button: int, screenX: int, screenY: int):
        qDebug('CanvasHandler::mousePressEvent()')
        # self._m_vtkFboItem.selectModel(screenX, screenY)

    @Slot(int, int, int)
    def mouseMoveEvent(self, button: int, screenX: int, screenY: int):
        qDebug('CanvasHandler::mouseMoveEvent()')

    @Slot(int, int, int)
    def mouseReleaseEvent(self, button: int, screenX: int, screenY: int):
        qDebug('CanvasHandler::mouseReleaseEvent()')


def main():
    app = App(sys.argv)
    engine = QQmlApplicationEngine()

    app.setApplicationName('vtkMolecule_QML')

    qmlRegisterType(FboItem, 'QtVTK', 1, 0, 'VtkFboItem')

    handler = canvasHandler()

    # Expose/Bind Python classes (QObject) to QML
    ctxt = engine.rootContext()  # returns QQmlContext
    ctxt.setContextProperty('canvasHandler', handler)

    # Load main QML file
    engine.load(QUrl.fromLocalFile('Mixed/main.qml'))

    app.setup(engine)
    handler.fbo = app._m_vtkFboItem

    rc = app.exec_()
    qDebug(f'CanvasHandler: Execution finished with return code: {rc}')


if __name__ == '__main__':
    main()
