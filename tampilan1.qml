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






Item {
    id: layar
    width: 1200
    height: 600
    visible: true

    function updateValue() {

         windSpeed_value.text = mqttvalue.windspeed()
         wind_direct_value.text = mqttvalue.winddirect()
         latitude_position_value.text = mqttvalue.lat()
         longitude_position_value.text = mqttvalue.long()
         heading_value.text = mqttvalue.headingship()
         vessel.rotation = mqttvalue.headingship()

         vessel1.x = mqttvalue.ship_x()
         vessel1.y = mqttvalue.ship_y()
        latitude_target.text = mqttvalue.lat_target()
        longtitude_target.text = mqttvalue.long_target()
        x_error.text= mqttvalue.long_error()
         y_error.text= mqttvalue.lat_error()


         speed1.text = mqttvalue.speedinput1()
         speed2.text = mqttvalue.speedinput2()
         speed3.text = mqttvalue.speedinput3()
         speed4.text = mqttvalue.speedinput4()

         gov1.active = mqttvalue.engineconect1()
         gov2.active = mqttvalue.engineconect2()
         gov3.active = mqttvalue.engineconect3()
         gov4.active = mqttvalue.engineconect4()

         dp1.text = mqttvalue.steering1()
         dp2.text = mqttvalue.steering2()
         dp3.text = mqttvalue.steering3()
         dp4.text = mqttvalue.steering4()

         arrowkiridepan.rotation = mqttvalue.steering1()
         arrowkanandepan.rotation = mqttvalue.steering4()

         arrowkananbelakang.rotation = mqttvalue.steering2()
         arrowkiribelakang.rotation = mqttvalue.steering3()

         volt1.text = mqttvalue.bat1()
         volt2.text = mqttvalue.bat2()
         volt3.text = mqttvalue.bat3()
         volt4.text = mqttvalue.bat4()

         rpm1.text = mqttvalue.mesin1()
         rpm2.text = mqttvalue.mesin2()
         rpm3.text = mqttvalue.mesin3()
         rpm4.text = mqttvalue.mesin4()

         suhu1.text = mqttvalue.temp1()
         suhu2.text = mqttvalue.temp2()
         suhu3.text = mqttvalue.temp3()
         suhu4.text = mqttvalue.temp4()

         connect1.active = mqttvalue.spc1()
         connect2.active = mqttvalue.spc2()
         connect3.active = mqttvalue.spc3()
         connect4.active = mqttvalue.spc4()


          dst_bw_line.text = mqttvalue.distance_bw_line()

    }




    Rectangle{
        id:mokup
        color: "black"
        anchors.fill: parent
        anchors.rightMargin: 8
        anchors.bottomMargin: 0
        anchors.leftMargin: -8
        anchors.topMargin: 0

        Image {
            id: backgroud
            x: -44
            y: -14
            width: 1404
            height: 654
            anchors.fill: parent
            source: "GUI DP Ponton.png"
            anchors.rightMargin: -96
            anchors.leftMargin: 17
            scale: 1.1
            anchors.bottomMargin: -130
            anchors.topMargin: 21

            Text {
                id: speed1
                x: 389
                y: 468
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            StatusIndicator {
                id: gov1
                x: 392
                y: 503
                width: 24
                height: 31
               active: true
                color: "red"
            }

            Text {
                id: speed2
                x: 389
                y: 571
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            StatusIndicator {
                id: gov2
                x: 392
                y: 606
                width: 24
                height: 31
               active: true
                color: "red"
            }

            Text {
                id: speed3
                x: 93
                y: 571
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            StatusIndicator {
                id: gov3
                x: 96
                y: 607
                width: 24
                height: 31
               active: true
                color: "red"
            }

            Text {
                id: speed4
                x: 93
                y: 468
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            StatusIndicator {
                id: gov4
                x: 96
                y: 502
                width: 24
                height: 31
               active: true
                color: "red"
            }

            Text {
                id: latitude_position_value
                x: 241
                y: 66
                width: 95
                height: 19
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: longitude_position_value
                x: 241
                y: 88
                width: 95
                height: 19
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: windSpeed_value
                x: 129
                y: 66
                width: 33
                height: 19
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: wind_direct_value
                x: 130
                y: 94
                width: 32
                height: 19
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: wind_direct_value1
                x: 160
                y: 91
                width: 32
                height: 19
                color: "#ffffff"
                text: qsTr("o")
                font.pixelSize: 11
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: windSpeed_value1
                x: 160
                y: 66
                width: 33
                height: 19
                color: "#ffffff"
                text: qsTr("kt")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: heading_value
                x: 250
                y: 109
                width: 65
                height: 60
                color: "#ffffff"
                text: qsTr("360")
                font.pixelSize: 24
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: wind_direct_value2
                x: 304
                y: 122
                width: 32
                height: 22
                color: "#ffffff"
                text: qsTr("o")
                font.pixelSize: 11
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: currentSpeed_value
                x: 131
                y: 119
                width: 33
                height: 19
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: windSpeed_value3
                x: 162
                y: 119
                width: 33
                height: 19
                color: "#ffffff"
                text: qsTr("kt")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: current_direct_value3
                x: 131
                y: 147
                width: 32
                height: 19
                color: "#ffffff"
                text: qsTr("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: wind_direct_value5
                x: 160
                y: 141
                width: 32
                height: 19
                color: "#ffffff"
                text: qsTr("o")
                font.pixelSize: 11
                font.styleName: "Bold"
                font.weight: Font.Bold
            }
        }


        ListModel{
            id: md
        }
        ListModel{
            id: md1
        }

         ListModel{
            id: md2
        }



        Plugin {
            id: mapPlugin
            name: "esri"
            PluginParameter { name: "osm.useragent"; value: "My great Qt OSM application" }
            PluginParameter { name: "osm.mapping.host"; value: "http://osm.tile.server.address/" }
            PluginParameter { name: "osm.mapping.copyright"; value: "All mine" }
            PluginParameter { name: "osm.routing.host"; value: "http://osrm.server.address/viaroute" }
            PluginParameter { name: "osm.geocoding.host"; value: "http://geocoding.server.address" }
            PluginParameter { name: "osm.mapping.providersrepository.address"; value: "satellite"}
        }



        Item {
              id: mapGroup
              x: 472
              y: 349
              width: 904
              height: 315
              property int count : 0
              property real lati : -6.000507
              property real longi : 106.687493




              Map{
                  id: map
                  x: -387
                  y: -28
                  width: 920
                  height: 506
                  color: "#f9f9f9"
                  anchors.rightMargin: 126
                  anchors.centerIn: parent;
                  anchors.fill: parent
                  anchors.verticalCenterOffset: 0
                  anchors.horizontalCenterOffset: 0
                  anchors.bottomMargin: -22
                  anchors.top: parent.top
                  anchors.topMargin: 0
                  anchors.left: parent.left
                  anchors.leftMargin: 0
                  maximumZoomLevel: 100.4
                  copyrightsVisible: true
                  antialiasing: true
                  maximumTilt: 89.3
                  plugin: mapPlugin
                  activeMapType: supportedMapTypes[1]

                  center: QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text)

                  gesture.enabled: true
                  gesture.acceptedGestures: MapGestureArea.PinchGesture | MapGestureArea.PanGesture



                  visible: true

                  Line{
                      id: li
                  }
                  Line1{
                      id: li1
                  }

                  Line2{
                      id: li2
                  }


                   Line3{
                       id:rpl_ondong_tahuna

                     }

                    Line4{
                        id:rpl_ondong_manado
                    }

                  Line5{
                      id:sanana_taliabu
                  }







                  Timer {

                      function updateloc() {
                          //var crd = map.toCoordinate(Qt.point(mouseX, mouseY))

                          //markerModel.append({ "latitude": lat.text, "longitude": lon.text})
                          if (li1.pathLength() < 500){
                              var text = md1.count + 1;

                              md1.append({"coords": QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text),
                               "title": text})



                              //console.log("coord = ", QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text))
                              //console.log("Banyak Tracker: ", li1.pathLength())
                              li1.addCoordinate(QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text))
                          }

                          if (li1.pathLength() >= 500){

                              for (var index = li1.pathLength(); index >= 0; index--)
                              {
                                  //console.log(li1.pathLength())
                                  li1.removeCoordinate([index]);

                                  //li.removeCoordinate(li.coordinateAt[index]);
                                  //console.log("Removing ", li.pathLength[index])
                                  //console.log(li.pathLength())
                              }
                          }
                      }
                      interval: 2000; running: true; repeat: true
                      onTriggered: {
                          updateloc()
                      }
                  }

                  MapItemView {
                      id: mivMarker

                      /*    add: Transition {
                          NumberAnimation {
                              property: "slideIn"
                              from: 50
                              to: 0
                              duration: 500
                              easing.type: Easing.OutBounce
                              easing.amplitude: 3.0
                          }
                      }*/

                      /*   remove: Transition {
                          NumberAnimation {
                              property: "opacity"
                              to: 0.1
                              duration: 50
                          }
                      }*/

                      model: ListModel {
                          id: markerModel
                      }

                      delegate: Component {


                          MapQuickItem {
                              coordinate: QtPositioning.coordinate(latitude, longitude)
                            //  anchorPoint: Qt.point(e1.width * 0.5, e1.height + slideIn)
                              property real slideIn : 0
                              /*         sourceItem: Shape {
                                  id: e1
                                  vendorExtensionsEnabled: false
                                  width: 32
                                  height: 32
                                  visible: true

                                  transform: Scale {
                                      origin.y: e1.height * 0.5
                                      yScale: -1
                                  }

                                  MouseArea{
                                      id: mousearea
                                      onPressed : {
                                          map.pressX = mouse.x
                                          map.pressY = mouse.y
                                          map.currentMarker = -1
                                          for (var i = 0; i< map.markers.length; i++){
                                              if (marker == map.markers[i]){
                                                  map.currentMarker = i
                                                  break
                                              }
                                          }
                                      }
                                  }

                          /*        ShapePath {
                                      id: c_sp1
                                      strokeWidth: -1
                                      fillColor: Qt.rgba(1,0,1,1.0)

                                      property real half: e1.width * 0.5
                                      property real quarter: e1.width * 0.25
                                      property point center: Qt.point(e1.x + e1.width * 0.5 , e1.y + e1.height * 0.5)


                                      property point top: Qt.point(center.x, center.y - half )
                                      property point bottomLeft: Qt.point(center.x - half, center.y + half )
                                      property point bottomRight: Qt.point(center.x + half, center.y + half )

                                      startX: center.x;
                                      startY: center.y + half

                                      PathLine { x: c_sp1.bottomLeft.x; y: c_sp1.bottomLeft.y }
                                      PathLine { x: c_sp1.top.x; y: c_sp1.top.y }
                                      PathLine { x: c_sp1.bottomRight.x; y: c_sp1.bottomRight.y }
                                      PathLine { x: c_sp1.center.x; y: c_sp1.center.y + c_sp1.half }
                                  } */                        }
                      }
                  }





//menampilkan koordinat sesuai mouse
                  MouseArea {
                      hoverEnabled: true
                      property var coordinate: map.toCoordinate(Qt.point(mouseX, mouseY))
                      x: 0
                      y: 0
                      width: 780
                      height: 331
                      anchors.rightMargin: -30
                      anchors.leftMargin: 19
                      anchors.fill: parent

                      Label
                      {
                          x: parent.mouseX - width
                          y: parent.mouseY - height - 5
                          text: "lat: %5; lon:%6".arg(parent.coordinate.latitude).arg(parent.coordinate.longitude)
                          color:"white"

                      }


                      property var panjanglintasan: li.pathLength()
                      property var path: li.path
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

                      onDoubleClicked: {
                          var coor = map.toCoordinate(Qt.point(mouseX, mouseY))
                          var text1 = md1.count + 1;
                          md1.append({"coords": coordinate, "title": text1})
                          li1.addCoordinate(coordinate)
                      }


                          }




//Kapal

                  MapQuickItem{
                      id : marker
                      sourceItem : Image{
                          id: imagenavigasi
                          width: 40
                          height: 37
                          //transformOrigin: Item.Center
                          source:"navigasi.png"
                          //rotation: 0
                          fillMode: Image.PreserveAspectFit
                          transform: [
                              Rotation {
                                  id: markerdirect
                                  origin.x: 15
                                  origin.y: 14
                                  angle: 0
                              }]
                      }
                      coordinate: QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text)
                      //coordinate: QtPositioning.coordinate(2.73706666666667, 125.36065)
                      anchorPoint.x : 15
                      anchorPoint.y : 14
                      //anchorPoint.x : parent
                      //anchorPoint.y : parent

                  }



                  Rectangle {
                      id: rectangle
                      x: 686
                      y: 282
                      width: 92
                      height: 47
                      color: "#a18cd1"
                      radius: 10
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

                      MouseArea{
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
                          horizontalAlignment: Text.AlignHCenter
                          font.pixelSize: 12
                      }

                      Text {
                          id: dst_bw_line
                          x: 44
                          y: -20
                          width: 40
                          height: 14
                          color: "#f7f7f7"
                          text: qsTr("0")
                          horizontalAlignment: Text.AlignRight
                          font.pixelSize: 12
                      }

                      Text {
                          id: element9
                          x: -116
                          y: -21
                          width: 117
                          height: 14
                          color: "#f9f9f9"
                          text: qsTr("Distance between line (m)")
                          horizontalAlignment: Text.AlignLeft
                          font.pixelSize: 12
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

                  }








                  MapQuickItem{
                      id : marker1

                      sourceItem : Image{
                          id: bouyondong
                          width: 40
                          height: 37
                          //transformOrigin: Item.Center
                          source:"bouy.png"
                          //rotation: 0
                          fillMode: Image.PreserveAspectFit

                      }



                      coordinate: QtPositioning.coordinate(3.572855377, 125.350032879)
                      //coordinate: QtPositioning.coordinate(2.73706666666667, 125.36065)
                      anchorPoint.x : 15
                      anchorPoint.y : 14

                  }






                  }
             }










        Item {
            id: stearing
            x: 475
            y: 73
            width: 782
            height: 258
              visible: strbutton.checked

            Image {
                id: strleft
                x: -200
                y: -150
                width: 665
                height: 604
                source: "steering.png"
                scale: 0.52
                fillMode: Image.Pad

                Image {
                    id: arrowkiridepan
                    anchors.fill: parent
                    horizontalAlignment: Image.AlignHCenter
                    source: "needle.png"
                    layer.format: ShaderEffectSource.RGBA
                    anchors.rightMargin: 49
                    anchors.bottomMargin: 77
                    anchors.leftMargin: 63
                    anchors.topMargin: -15
                    transformOrigin: Item.Center


                    scale: 1
                    rotation: 0
                    fillMode: Image.PreserveAspectFit

                }

                Image {
                    id: arrowkanandepan
                    anchors.fill: parent
                    horizontalAlignment: Image.AlignHCenter
                    source: "yellow.png"
                    anchors.leftMargin: 63
                    rotation: 90
                    fillMode: Image.PreserveAspectFit
                    transformOrigin: Item.Center
                    anchors.rightMargin: 49
                    layer.format: ShaderEffectSource.RGBA
                    anchors.bottomMargin: 77
                    scale: 1
                    anchors.topMargin: -15
                }
            }

            Image {
                id: strright
                x: 315
                y: -149
                width: 665
                height: 604
                source: "steering.png"
                fillMode: Image.Pad
                scale: 0.52


                Image {
                    id: arrowkiribelakang
                    anchors.fill: parent
                    horizontalAlignment: Image.AlignHCenter
                    source: "needle.png"
                    anchors.leftMargin: 63
                    rotation: 0
                    fillMode: Image.PreserveAspectFit
                    transformOrigin: Item.Center
                    anchors.rightMargin: 49
                    layer.format: ShaderEffectSource.RGBA
                    anchors.bottomMargin: 77
                    scale: 1
                    anchors.topMargin: -15
                }

                Image {
                    id: arrowkananbelakang
                    anchors.fill: parent
                    horizontalAlignment: Image.AlignHCenter
                    source: "yellow.png"
                    anchors.leftMargin: 63
                    rotation: 90
                    anchors.rightMargin: 49
                    transformOrigin: Item.Center
                    fillMode: Image.PreserveAspectFit
                    layer.format: ShaderEffectSource.RGBA
                    anchors.bottomMargin: 77
                    scale: 1
                    anchors.topMargin: -15
                }
            }

            Text {
                id: text1
                x: 343
                y: 8
                color: "#ffffff"
                text: qsTr("STEERING")
                font.pixelSize: 20
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: text2
                x: 271
                y: 43
                color: "#fffe00"
                text: qsTr("DP 1  :")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: text3
                x: 271
                y: 206
                color: "#ef4035"
                text: qsTr("DP 4  :")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: dp1
                x: 370
                y: 44
                color: "#fffe00"
                text: qsTr("0")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: dp4
                x: 373
                y: 206
                color: "#ef4035"
                text: qsTr("0")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: text6
                x: 385
                y: 88
                color: "#fffe00"
                text: qsTr("DP 2  :")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: dp2
                x: 484
                y: 89
                color: "#fffe00"
                text: qsTr("0")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: text8
                x: 386
                y: 146
                color: "#ef4035"
                text: qsTr("DP 3  :")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

            Text {
                id: dp3
                x: 484
                y: 146
                width: 15.775
                color: "#ef4035"
                text: qsTr("0")
                font.pixelSize: 26
                font.styleName: "Bold"
                font.weight: Font.ExtraBold
            }

        }

        Item {
            id: electical
            x: 475
            y: 73
            width: 782
            height: 258
            visible: elecbutton.checked
            Rectangle{
                width: 20
                height: 20
                color: "blue"
            }

            Image {
                id: image
                x: -103
                y: -255
                width: 975
                height: 1094
                source: "status.png"
                fillMode: Image.Stretch

                Text {
                    id: volt1
                    x: 164
                    y: 299
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.styleName: "Bold"
                    transformOrigin: Item.Center
                }

                Text {
                    id: volt2
                    x: 387
                    y: 299
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: volt3
                    x: 584
                    y: 299
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: volt4
                    x: 774
                    y: 299
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: rpm1
                    x: 159
                    y: 354
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("1000")
                    font.pixelSize: 23
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: rpm2
                    x: 382
                    y: 354
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("1000")
                    font.pixelSize: 23
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: rpm3
                    x: 577
                    y: 354
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("1000")
                    font.pixelSize: 23
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: rpm4
                    x: 764
                    y: 354
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("1000")
                    font.pixelSize: 23
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: suhu1
                    x: 157
                    y: 413
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: suhu2
                    x: 382
                    y: 413
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: suhu3
                    x: 584
                    y: 413
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                Text {
                    id: suhu4
                    x: 774
                    y: 413
                    width: 88
                    height: 32
                    color: "#ffffff"
                    text: qsTr("12")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    transformOrigin: Item.Center
                    font.styleName: "Bold"
                }

                StatusIndicator {
                    id: connect1
                    x: 200
                    y: 475
                    width: 29
                    height: 25
                    active: true
                    color: "green"
                }

                StatusIndicator {
                    id: connect2
                    x: 426
                    y: 475
                    width: 29
                    height: 25
                    color: "#008000"
                    active: true
                }

                StatusIndicator {
                    id: connect3
                    x: 619
                    y: 475
                    width: 29
                    height: 25
                    color: "#008000"
                    active: true
                }

                StatusIndicator {
                    id: connect4
                    x: 809
                    y: 475
                    width: 29
                    height: 25
                    color: "#008000"
                    active: true
                }
            }
        }

        Item {
            id: positionkeep
            x: 475
            y: 71
            width: 782
            height: 258
            visible: posbutton.checked

            Image {
                id: image1
                x: -140
                y: -293
                width: 966
                height: 1094
                source: "positioning.png"
                fillMode: Image.Stretch

                Item {
                    id: item1
                    x: 140
                    y: 294
                    width: 441
                    height: 263

                    Image {
                        id: vessel1
                        x: 187
                        y: 98
                        width: 83
                        height: 66
                        source: "CHH.png"
                        fillMode: Image.PreserveAspectFit
                        rotation: 0
                    }
                }

                Text {
                    id: text4
                    x: 720
                    y: 296
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("Positioning Target")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    font.styleName: "Bold"
                    font.weight: Font.Bold
                    font.bold: true
                }

                Text {
                    id: text5
                    x: 597
                    y: 340
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr(" Latitude      :")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: text7
                    x: 597
                    y: 375
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr(" Longtitude :")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: text10
                    x: 703
                    y: 419
                    width: 94
                    height: 28
                    color: "#ffffff"
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: text9
                    x: 721
                    y: 423
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("Positioning Error")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: text11
                    x: 631
                    y: 459
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("X :                              m")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: text12
                    x: 630
                    y: 504
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("Y :                              m")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: latitude_target
                    x: 703
                    y: 341
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("Latitude Target")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignLeft
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: longtitude_target
                    x: 703
                    y: 375
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("Longtitude Target")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignLeft
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: x_error
                    x: 635
                    y: 460
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("0")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignLeft
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }

                Text {
                    id: y_error
                    x: 635
                    y: 505
                    width: 94
                    height: 28
                    color: "#ffffff"
                    text: qsTr("0")
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignLeft
                    font.weight: Font.Bold
                    font.styleName: "Bold"
                    font.bold: true
                }
            }

            Rectangle {
                id: rectangle3
                x: 530
                y: 23
                width: 200
                height: 2
                color: "#ffffff"
            }

            Rectangle {
                id: rectangle1
                x: 530
                y: 153
                width: 200
                height: 2
                color: "#ffffff"
            }
        }

        TabButton {
            id: strbutton
            x: 474
            y: 51
            width: 63
            height: 19
           // visible: false
            text: qsTr("Tab Button")
            checked: false
            checkable: true
            opacity: 0
        }

        TabButton {
            id: elecbutton
            x: 549
            y: 51
            width: 63
            height: 16
           // visible: false
            text: qsTr("Tab Button")
            checked: false
            checkable: true
               opacity: 0
        }

        TabButton {
            id: posbutton
            x: 625
            y: 51
            width: 63
            height: 16
            // visible: false
            text: qsTr("Tab Button")
            checked: false
            checkable: true
            opacity: 0
        }

        Image {
            id: vessel
            x: 134
            y: 225
            width: 190
            height: 166
            source: "CHH.png"
            rotation: 0
            fillMode: Image.PreserveAspectFit
        }
    }


}




/*##^##
Designer {
    D{i:0;formeditorZoom:0.2}
}
##^##*/
