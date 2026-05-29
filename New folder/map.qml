import QtQuick.Window 2.1
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Extras 1.4
import QtQuick.Controls.Styles.Desktop 1.0
import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0

import QtQuick.Layouts 1.1
import QtLocation 5.11
import QtPositioning 5.0

import QtQuick.Window 2.3

import QtGraphicalEffects 1.0
import QtQuick.Controls.Imagine 2.3
import QtQuick.Controls.Material 2.0



import QtQuick 2.7
Map {
    id: map
    x: -387
    y: -28
    width: 920
    height: 506
    visible: true
    color: "#f9f9f9"
    anchors.left: parent.left
    anchors.top: parent.top
    anchors.fill: parent
    plugin: mapPlugin
    gesture.acceptedGestures: MapGestureArea.PinchGesture | MapGestureArea.PanGesture
    activeMapType: supportedMapTypes[1]
    anchors.centerIn: parent
    center: QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text)
    anchors.rightMargin: 126
    gesture.enabled: true
    copyrightsVisible: true
    anchors.topMargin: 0
    anchors.verticalCenterOffset: 0
    anchors.leftMargin: 0
    anchors.horizontalCenterOffset: 0
    maximumZoomLevel: 100.4
    maximumTilt: 89.3
    anchors.bottomMargin: -22
    antialiasing: true

    Line {
        id: li
    }

    Line1 {
        id: li1
    }

    Line2 {
        id: li2
    }

    Line3 {
        id: rpl_ondong_tahuna
    }

    Line4 {
        id: rpl_ondong_manado
    }

    Line5 {
        id: sanana_taliabu
    }

    Timer {
        running: true
        onTriggered: {
            updateloc()
        }
        repeat: true
        interval: 2000
    }

    MapItemView {
        id: mivMarker
        delegate: Component {
            MapQuickItem {
                coordinate: QtPositioning.coordinate(latitude, longitude)
                property real slideIn: 0
            }
        }
        model: ListModel {
            id: markerModel
        }
    }

    MouseArea {
        x: 0
        y: 0
        width: 780
        height: 331
        anchors.fill: parent
        anchors.leftMargin: 19
        path: li.path
        Label {
            x: parent.mouseX - width
            y: parent.mouseY - height - 5
            color: "#ffffff"
            text: "lat: %5; lon:%6".arg(parent.coordinate.latitude).arg(parent.coordinate.longitude)
        }
        onDoubleClicked: {
            var coor = map.toCoordinate(Qt.point(mouseX, mouseY))
            var text1 = md1.count + 1;
            md1.append({"coords": coordinate, "title": text1})
            li1.addCoordinate(coordinate)
        }
        coordinate: map.toCoordinate(Qt.point(mouseX, mouseY))
        anchors.rightMargin: -30
        hoverEnabled: true
        onPressAndHold: {
            var crd = map.toCoordinate(Qt.point(mouseX, mouseY))

            if (md.count < 1){
                mqttvalue.get_lat(crd.latitude)
                mqttvalue.get_lon(crd.longitude)
            }
            else if (md.count > 0){
                mqttvalue.get_lat1(crd.latitude)
                mqttvalue.get_lon1(crd.longitude)
            }

            markerModel.append({ "latitude": crd.latitude, "longitude": crd.longitude})
            var text = md.count + 1;
            md.append({"coords": coordinate, "title": text})
            li.addCoordinate(coordinate)

            if (Math.abs(map.pressX - mouse.x ) < map.jitterThreshold
                    && Math.abs(map.pressY - mouse.y ) < map.jitterThreshold) {
                var p = map.fromCoordinate(crd)
                lastX = p.x
                lastY = p.y
                //map.showMarkerMenu(marker.coordinate)
            }
        }
        panjanglintasan: li.pathLength()
    }

    MapQuickItem {
        id: marker
        sourceItem: Image {
            id: imagenavigasi
            width: 40
            height: 37
            source: "navigasi.png"
            fillMode: Image.PreserveAspectFit
            transform: [
                Rotation {
                    id: markerdirect
                    angle: 0
                    origin.y: 14
                    origin.x: 15
                }]
        }
        coordinate: QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text)
        anchorPoint.x: 15
        anchorPoint.y: 14
    }

    Rectangle {
        id: rectangle
        x: 686
        y: 282
        width: 92
        height: 47
        color: "#a18cd1"
        radius: 10
        MouseArea {
            x: 0
            y: 0
            width: 92
            height: 47
            onDoubleClicked: {
                markerModel.clear()
                mqttvalue.get_lat(0)
                mqttvalue.get_lon(0)
                mqttvalue.get_lat1(0)
                mqttvalue.get_lon1(0)
                md.clear()
                //md.count = 0
                for (var index = li.pathLength(); index >= 0; index--)
                {
                    //console.log(li.pathLength())
                    li.removeCoordinate([index]);
                    li1.removeCoordinate([index]);
                    //li.removeCoordinate(li.coordinateAt[index]);
                    //console.log("Removing ", li.pathLength[index])
                    //console.log(li.pathLength())
                }
            }
        }

        Text {
            id: element
            x: 0
            y: 15
            width: 92
            height: 14
            text: qsTr("Clear line")
            font.pixelSize: 12
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            id: dst_bw_line
            x: 44
            y: -20
            width: 40
            height: 14
            color: "#f7f7f7"
            text: qsTr("0")
            font.pixelSize: 12
            horizontalAlignment: Text.AlignRight
        }

        Text {
            id: element9
            x: -116
            y: -21
            width: 117
            height: 14
            color: "#f9f9f9"
            text: qsTr("Distance between line (m)")
            font.pixelSize: 12
            horizontalAlignment: Text.AlignLeft
        }

        Text {
            id: markerinfo
            x: -116
            y: -41
            width: 117
            height: 14
            color: "#f9f9f9"
            text: qsTr("Marker Info")
            font.pixelSize: 12
            horizontalAlignment: Text.AlignLeft
        }
        gradient: Gradient {
            GradientStop {
                position: 0
                color: "#84fab0"
            }

            GradientStop {
                position: 1
                color: "#8fd3f4"
            }
        }
    }

    MapQuickItem {
        id: marker1
        sourceItem: Image {
            id: bouyondong
            width: 40
            height: 37
            source: "bouy.png"
            fillMode: Image.PreserveAspectFit
        }
        coordinate: QtPositioning.coordinate(3.572855377, 125.350032879)
        anchorPoint.x: 15
        anchorPoint.y: 14
    }
}
