import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtCharts 2.3
import QtVTK 1.0

ApplicationWindow {
    id: root
    minimumWidth: 1024
    minimumHeight: 700
    visible: true
    title: "QtVTK-Py"

    Material.primary: Material.Indigo
    Material.accent: Material.LightBlue

    Rectangle {
        id: screenCanvasUI
        anchors.fill: parent

        VtkFboItem {
            id: vtkFboItem
            objectName: "vtkFboItem"
            anchors.fill: parent

            MouseArea {
                acceptedButtons: Qt.AllButtons
                anchors.fill: parent
                scrollGestureEnabled: false

                onPositionChanged: (mouse) => {
                    canvasHandler.mouseMoveEvent(pressedButtons, mouseX, mouseY);
                   mouse.accepted = false;
                }
                onPressed: (mouse) => {
                    canvasHandler.mousePressEvent(pressedButtons, mouseX, mouseY);
                    mouse.accepted = false;
                    // if u want to propagate the pressed event
                    // so the VtkFboItem instance can receive it
                    // then uncomment the belowed line
                    // mouse.ignore() // or mouse.accepted = false
                }
                onReleased: (mouse) => {
                    canvasHandler.mouseReleaseEvent(pressedButtons, mouseX, mouseY);
                    print(mouse);
                    mouse.accepted = false;
                }
                onWheel: (wheel) => {
                    wheel.accepted = false;
                }
            }
        }

        Button {
            id: clearScene
            text: "Clear Scene"
            highlighted: true
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 50
            onClicked: canvasHandler.clearScene()

            ToolTip.visible: hovered
            ToolTip.delay: 1000
            ToolTip.text: "Show 2D Chart in right corner"
        }

        Button {
            id: createScene
            text: "Create Lattice"
            highlighted: true
            anchors.right: clearScene.left
            anchors.bottom: parent.bottom
            anchors.margins: 50
            onClicked: canvasHandler.create_structure()

            ToolTip.visible: hovered
            ToolTip.delay: 1000
            ToolTip.text: "Open a 3D model into the canvas"
        }



    }

    FileDialog {
        id: openModelsFileDialog
        visible: false
        title: "Import model"
        folder: shortcuts.documents
        nameFilters: ["Model files" + "(*.stl *.STL)", "All files" + "(*)"]

        onAccepted: {
            canvasHandler.showFileDialog = false;
            canvasHandler.openModel(fileUrl);
        }
        onRejected: {
            canvasHandler.showFileDialog = false;
        }
    }
}