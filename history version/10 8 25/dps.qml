/*
import QtQuick.Window 2.2 //2.1
import QtQuick.Controls 1.4 //1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Extras 1.4
import QtQuick.Controls.Styles.Desktop 1.0
import QtQuick 2.12 //2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.1
import QtLocation 5.11
import QtPositioning 5.8
import QtQuick.Window 2.3
import QtGraphicalEffects 1.0
import QtQuick.Controls.Imagine 2.3
import QtQuick.Controls.Material 2.0
import QtQuick 2.7
//import QtWebEngine 1.0

import QtCharts 2.1
import "controls"
import QtQuick.Shapes 1.14

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3
import Qt.labs.folderlistmodel 2.1

*/

import QtQuick.Window 2.2 //2.1
import QtQuick.Controls 1.4 //1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Extras 1.4
import QtQuick.Controls.Styles.Desktop 1.0
import QtQuick 2.12 //2.12
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
//import QtWebEngine 1.0
import QtCharts 2.1
import QtQuick.Shapes 1.14
import "controls"
import QtQuick.Extras 1.4
import QtQuick.Extras.Private 1.0
import QtQuick.Dialogs 1.0
import PyCVQML 1.0

Window {
	id : root
	width: 1024
	height: 700
	color : "#0C2D57"
	title:"DPS SYERGIE"
    visible: true
    //flags: Qt.WindowMaximized //Qt.Dialog
	property var navigation_mode_var;
	property var navigation_mode_var_prev;
	
	property var points: []
	property var points2:[]
	
	property var power_color;
	property double ruler_count;
	property double ruler_measurement;

	property double lat1;
	property double long1;
	property double lat2;
	property double long2;

	// Define the textData property to hold the text from the TextFields
    property var textData: [];

	property var fsm_data1: [];

	function toRadians(degrees) {
        return degrees * Math.PI / 180.0;
    }


	function mapValue(x, in_min, in_max, out_min, out_max){
		return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
	}

	function constrain(x, min, max){
		if (x > max){
			x = max
		}

		if (x < min){
			x = min
		}
		return x
	}
	
	
	function rot_matrice(x, y, theta) {
        var radians = toRadians(theta);
        var cosTheta = Math.cos(radians);
        var sinTheta = Math.sin(radians);

        var jTheta = [
            [cosTheta, -sinTheta, 0],
            [sinTheta, cosTheta, 0],
            [0, 0, 1]
        ];

        var result = [
            jTheta[0][0] * x + jTheta[0][1] * y + jTheta[0][2] * theta,
            jTheta[1][0] * x + jTheta[1][1] * y + jTheta[1][2] * theta,
            jTheta[2][0] * x + jTheta[2][1] * y + jTheta[2][2] * theta
        ];

        var x_accent = result[1];
        var y_accent = result[0];

        return { x_accent: x_accent, y_accent: y_accent };
    }


	function meter_conversion(lat1, long1, lat2, long2) {
        var delta_lat = (lat1 - lat2) * 111000
        var delta_long = (long1 - long2) * 111000
        var distance = Math.sqrt(Math.pow(delta_lat, 2) + Math.pow(delta_long, 2))
        return distance
    }


	function upload_csv() {
		console.log("uploading csv....")
		markerModel.clear()
		md.clear()
		backend.line_reset(0)
			   
		for (var index = li.pathLength(); index >= 0; index--){
            li.removeCoordinate([index]);
            li1.removeCoordinate([index]);
                                    
        }

        for (var i = 0; i < rpl_lat.length; i++) {
		
			var coordinate = QtPositioning.coordinate(rpl_lat[i], rpl_long[i]);
			markerModel.append({"latitude": rpl_lat[i], "longitude": rpl_long[i]});
			var text = md.count + 1;
			md.append({"coords": coordinate, "title": text});
			li.addCoordinate(coordinate)

		}

	}

	Rectangle {
    id: layar
    width: 1200
    height: 600
    visible: true

    

    Rectangle{
        id:mokup
        color: "black"
        anchors.fill: parent
        anchors.rightMargin: 8
        anchors.bottomMargin: 0
        anchors.leftMargin: -8
        anchors.topMargin: 0
		
		
		
        Rectangle {
            id: backgroud
            x: -44
            y: -14
            width: 1404
            height: 654
            anchors.fill: parent
            //source: "GUI DP Ponton versi 2.png"
            anchors.rightMargin: -117
            anchors.leftMargin: 7
            scale: 1.1
            anchors.bottomMargin: -74
            anchors.topMargin: 21
			color :"#0C2D57"
		
		
		
		
		
		
		Image {
			x : 70
			y: 0
			width : 70
			height : 70
			source :"anemometer.png"
		
		
		}
		
		
		
		
		
		//GARIS GARIS 
		
		Rectangle{
			x: 0
			y : 65
			width : 1380
			height : 3
			color : "#00ff00"
			visible : true
			
		}
		
		Rectangle{
			x: 200
			y : 0
			width : 3
			height : 68
			color : "#00ff00"
			visible : true
			
		}
		
		Rectangle{
			x: 0
			y : 270
			width : 375
			height : 3
			color : "#00ff00"
			visible : true
			
		}
		
		Rectangle{
			x: 0
			y : 665
			width : 375
			height : 3
			color : "#00ff00"
			visible : true
			
		}
		
		Rectangle{
			x: 350
			y : 0
			width : 3
			height : 68
			color : "#00ff00"
			visible : true
			
		}
		
		
		Rectangle{
			x: 500
			y : 0
			width : 3
			height : 68
			color : "#00ff00"
			visible : true
			
		}
		
		Rectangle{
			x: 715
			y : 0
			width : 3
			height : 68
			color : "white"
			visible : true
			
		}

		Rectangle{
			x: 850
			y : 0
			width : 3
			height : 68
			color : "#00ff00"
			visible : true
			
		}

		Rectangle{
			x: 375
			y : 65
			width : 3
			height : 605
			color : "#00ff00"
			visible : true
			
		}
		
		
		
		////////////////////
		Image {
			x : 500
			y: 4
			width : 90
			height : 70
			source :"mapicon.png"
		
		
		}
		
		Image {
			x : 370
			y: 20
			width : 40
			height : 40
			source :"speedo.png"
		
		
		}
		

            Text {
                id: latitude_position_value
                x: 600
                y: 17
                width: 95
                height: 19
                color: "white"
                text: ("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

			 Text {
                id: latitude_destination
                x: 600
                y: 17
                width: 95
                height: 19
                color: "white"
                text: ("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
				visible : false
            }

			Text {
                id: longitude_destination
                x: 600
                y: 17
                width: 95
                height: 19
                color: "white"
                text: ("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
				visible : false
            }

            Text {
                id: longitude_position_value
                x: 600
                y: 37
                width: 95
                height: 19
                color: "#ffffff"
                text: ("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }


			Text {
						id : lat_long_dms_text
						x : 730
						y : 17
						text : "lat dms"
						color: "#ffffff"
						font.pixelSize: 16
						font.family: "Helvetica"
						font.bold : true
					}
            Text {
                id: windSpeed_value
                x: 136
                y: 17
                width: 33
                height: 19
                color: "#ffffff"
                text: ""
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: wind_direct_value
                x: 138
                y: 42
                width: 32
                height: 19
                color: "#ffffff"
                text: ("100")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: wind_direct_value1
                x: 168
                y: 39
                width: 32
                height: 19
                color: "#ffffff"
                text: ("o")
                font.pixelSize: 11
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: windSpeed_value1
                x: 167
                y: 17
                width: 33
                height: 19
                color: "#ffffff"
                text: ("kt")
                font.pixelSize: 16
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            Text {
                id: heading_value
                x: 260
                y: 11
                width: 65
                height: 60
                color: "#ffffff"
                text: ("360")
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.styleName: "Bold"
                font.weight: Font.Bold
            }


		
		Image {
			x : 220
			y: 13
			width : 50
			height : 50
			source :"compass.png"
		
		
		}
	//control heading
	Rectangle {
		x:90
		y:100
        width: 100
        height: 100
        //anchors.top : parent.top
        //anchors.topMargin: 300
        //anchors.left : parent.left
        //anchors.leftMargin: 50
        visible: true
        color: "#00000000"
		
		
		
		CircularSlider {
				id: slider
				x: 0
				y: 0
				handleVerticalOffset: -30
				trackWidth: 2
				trackColor: "transparent"
				width: parent.width
				height: parent.height
				minValue: 0
				maxValue: 360
				value: 0
				snap: true
				stepSize: 1
				hideProgress: true
				hideTrack: true
				interactive: true
				
				visible : true//heading_keeping_button.checked || station_keeping_button.checked

				/// Custom Handle
				handle: Item {
					id: item
				
					width: 10
					height: 10

					Rectangle{
					width : parent.width
					height : parent.height
					radius : width/2
					color : "#D95204"
					}	

					transform: Translate {
						x: (slider.handleWidth - width) / 2
						y: (slider.handleHeight - height) / 2
					}
				}


				Repeater {
					model: 0
					visible : false

					delegate: Rectangle {
						anchors.centerIn: parent
						height: slider.height
						width: 1
						color: "black"
						transform: Rotation {
							origin.x: 1
							origin.y: slider.height / 2
							angle: 30 * index
						}
					}
				}

				/// Inner Trinagle
				Shape {
					id: triangle
					width: 30
					height: parent.height / 2 - 0
					x: (parent.width - width) / 2
					y: 0
					transform: Rotation {
						origin.x: triangle.width / 2
						origin.y: triangle.height
						angle: slider.angle
					}

					ShapePath {
						strokeWidth: 1
						strokeColor: "#D95204"
						fillColor: "#D95204"
						startX: triangle.width / 2
						startY: 0

						PathLine { x: 0; y: triangle.height }
						PathLine { x: triangle.width; y: triangle.height }
						PathLine { x: triangle.width/2; y: 0 }
					}
				}

				/// Inner Circle
				Rectangle {
					color: "#D95204"
					width: 40
					height: width
					radius: width / 2
					anchors.centerIn: parent
					
					Label {
						anchors.centerIn: parent
						visible : false
						font.pointSize: 12
						color: "#FEFEFE"
						text: slider.value === 0 ? Number(12) : Number(slider.value).toString().padStart(2, '0')
					}
				}

				/// Outer Dial
				Rectangle {
					anchors.fill: parent
					color: "transparent"
					border.color: "#595959"
					border.width: 6
					visible : false
					radius: width / 2

				}

            
               
        }


	}
	
	///////////
	
	//compass widget
	Rectangle {
		x:90
		y:100
        width: 100
        height: 100
        //anchors.top : parent.top
        //anchors.topMargin: 300
        //anchors.left : parent.left
        //anchors.leftMargin: 50
        visible: true
        color: "#00000000"
		
		
		Label {
					y : 140
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 18
					
                    color: "white"
                    text: "COMPASS"
                }


		Text {
				id : compass_val
				y : 120
                anchors.horizontalCenter: parent.horizontalCenter

                color: "#ffffff"
                text: slider.value
                font.pixelSize: 14
                font.styleName: "Bold"
                font.weight: Font.Bold
            }
			
		
		Text{
			id : yaw
			visible : false
			text : heading_value.text
			
		}
		
		
		Text {
                text: "N"
                color: "#00ff00"
                font.pixelSize: 17
                anchors.bottom: parent.top
                anchors.bottomMargin: 1
                anchors.horizontalCenter: parent.horizontalCenter
            }
		
		Label {
                text: "E"
                color: "#00ff00"
                font.pixelSize: 17
                anchors.left: parent.right
                anchors.leftMargin: 5
                anchors.verticalCenter: parent.verticalCenter
            }

        Label {
                text: "S"
                color: "#00ff00"
                font.pixelSize: 17
                anchors.top: parent.bottom
                anchors.topMargin: 1
                anchors.horizontalCenter: parent.horizontalCenter
            }

        Label {
                text: "W"
                color: "#00ff00"
                font.pixelSize: 17
                anchors.right: parent.left
                anchors.rightMargin: 5
                anchors.verticalCenter: parent.verticalCenter
            }
		
		
		
		
		Rectangle {
			x:0
			y:0
			width: parent.width
			height: parent.height
			//anchors.top : parent.top
			//anchors.topMargin: 300
			//anchors.left : parent.left
			//anchors.leftMargin: 50
        visible: true
        color: "#00000000"
		rotation : yaw.text
		
		}
		
		Rectangle {
			x:0
			y:0
			width: parent.width
			height: parent.height
			//anchors.top : parent.top
			//anchors.topMargin: 300
			//anchors.left : parent.left
			//anchors.leftMargin: 50
        visible: true
        color: "#00000000"
		rotation : yaw.text
		
		
		
		CircularSlider {
            id: compass

            handleVerticalOffset: -30
            trackWidth: 5
            trackColor: "#FEFEFE"
            width: parent.width
            height: parent.height
            minValue: 0
            maxValue: 360
            value: 0//yaw.text//40
            snap: true
            stepSize: 1
            hideProgress: true
            hideTrack: true
            interactive: false
            
			
			Behavior on value {
				NumberAnimation {
					duration: 900
				}
			}

            /// Custom Handle
            handle: Item {
                id: item

                width: 24
                height: 24

                Shape {
                    anchors.fill: parent
                    rotation: 180

                    ShapePath {
                        strokeWidth: 1
                        strokeColor: "#FF5555"
                        fillColor: "#FF5555"
                        startX: item.width / 2
                        startY: 0

                        PathLine { x: 0; y: item.height }
                        PathLine { x: item.width; y: item.height }
                        PathLine { x: item.width/2; y: 0 }
                    }
                }

                transform: Translate {
                    x: (compass.handleWidth - width) / 2
                    y: (compass.handleHeight - height) / 2
                }
            }

          /// Inner Trinagle
            Shape {
                id: triangle_compass
                width: 20
                height: parent.height / 2
                x: (parent.width - width ) / 2
                y: 0
                transform: Rotation {
                    origin.x: triangle_compass.width / 2
                    origin.y: triangle_compass.height
                    angle: compass.angle
                }

                ShapePath {
                    strokeWidth: 0
                    strokeColor: "#00ff00"
                    fillColor: "#00ff00"//"#50FA7B"
                    startX: triangle_compass.width / 2
                    startY: 0

                    PathLine { x: 0; y: triangle_compass.height }
                    PathLine { x: triangle_compass.width; y: triangle_compass.height }
                    PathLine { x: triangle_compass.width/2; y: 0 }
                }
            }

            /// Inner Circle
            Rectangle {
                color: "transparent"//"#232323"
                width: 120
                height: width
                radius: width / 2
                anchors.centerIn: parent
				//rotation : yaw.text 
                
            }

            /// Outer Dial
            Rectangle {
                anchors.fill: parent
                color: "transparent"
                border.color: "#00ff00"
                border.width: 4
                radius: width / 2
				
            }

            
            

           
        }
        
		
		
		Rectangle {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter 
			//y: 220
			width: 0.26*parent.width
			height: 0.13*parent.width
			color: "#00000000"
			visible : false
			Text {
				
				anchors.horizontalCenter: parent.horizontalCenter
				y: 0.6*parent.width
				text: "degree"
				font.family: "Helvetica"
				font.pixelSize: Math.max(6, parent.width * 0.2)
				color: "#e5e5e5"
			}
		}
		
		
            
	
	
	}
	
	//labels
	Rectangle{
		anchors.centerIn: parent
		width : 30
		height : 30
		border.color : "gold"
		border.width : 2
		radius : width/2
		color : "#00ff00"
		
		
	Label {
                    anchors.centerIn: parent
                    font.pixelSize: 15
                    color: "black"
                    text: Math.floor(yaw.text)
                }
				
	}

	}    
	////////////////
		
	
	//gyroscope widget
	Text {
			id : roll
			x : 35
			y : 510
			text: "000"
			color: "#e85d08"
			font.pixelSize: 75
			rotation:0
			//font.bold : true
			visible : false
		}	
		
	Rectangle {
        x: 220
		y: 80
		width: 150
        height: 150
        //anchors.top : parent.top
        //anchors.topMargin: 300
        //anchors.left : parent.left
        //anchors.leftMargin: 560
        visible: true
        color: "transparent"
		
		Label {
					y : 150
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 20
					
                    color: "white"
                    text: "GYROSCOPE"
                }
		
        CircularSlider {
            id: roll_gauge
            hideProgress: true
            hideTrack: true
            width: parent.width
            height: parent.height

            handleColor: "#e85d08"//"#6272A4"
            handleWidth: 32
            handleHeight: 32
            minValue: 0
            maxValue: 1000
			value :roll.text//0
            interactive: false
            
            Behavior on value {
				NumberAnimation {
					duration: 900
				}
			}

            // Custom progress Indicator
            Item {
                anchors.fill: parent
                anchors.margins: 5
                Rectangle{
                    id: mask1
                    anchors.fill: parent
                    radius: parent.width / 2
                    color: "#e85d08"//"#282A36"
                    border.width: 5
                    border.color: "#44475A"
                }

                Item {
                    anchors.fill: mask1
                    anchors.margins: 5
                    layer.enabled: true
                    rotation: roll_gauge.value // 10 - 50
                    layer.effect: OpacityMask {
                        maskSource: mask1
                    }
                    Rectangle {
                        height: parent.height  //roll_gauge.value / roll_gauge.maxValue
                        width: parent.width
                        color:"#0C2D57"//"#5B99A6"
                    }
					
					
                    Image {
						
                        id: icon2
						
						y: (1 * parseInt(pitch_filtered_sensor.text)) - 90  //y = -90 alpha = 0  y = -10 alpha = -90 y = -170
						width :  parent.width + 180
						height : parent.height + 180 
                        //anchors.fill: parent
                        source: "rollbackground.png"
                        }
					
                }

                Label {
					x:75
					//anchors.centerIn: parent
                    //anchors.horizontalCenter: parent.horizontalCenter
                    y: 10//0.2*parent.width
                    font.pixelSize: 12
                    color: "white"//"#404040"
                    text: (Number(roll_gauge.value).toFixed() + "°")
                    //text: roll_gauge.value //Number(Math.abs(roll_gauge.value/10-50)).toFixed()
                }
				
				Label {
					id : pitch_filtered_sensor
                    x: 75
					//anchors.centerIn: parent
                    //anchors.horizontalCenter: parent.horizontalCenter
                    y: 0.2*parent.width + 30
                    font.pixelSize: 12
                    color: "white"//"#404040"
                    text: "0"+ "°"
                    //text: roll_gauge.value //Number(Math.abs(roll_gauge.value/10-50)).toFixed()
                }
				
				
                Rectangle {
					anchors.horizontalCenter: parent.horizontalCenter
					anchors.verticalCenter: parent.verticalCenter 
					//y: 220
					width: 0.26*parent.width
					height: 0.13*parent.width
					color: "#00000000"
					Text {
						anchors.horizontalCenter: parent.horizontalCenter
						y: parent.width - 20
						text: ""
						font.family: "Helvetica"
						font.pixelSize: Math.max(6, parent.width * 0.5)
						
						color: "white"
					}
				}
            
			
			Image {
                        
						//width :  50
						//height : 40
                        anchors.fill: parent
                        source: "roll.png"
                        }
			
			}
            Label {
                text: ""
                color: "#00A5FF"
                font.pixelSize: 16
                anchors.bottom: roll_gauge.top
                anchors.bottomMargin: 10
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
	/////////
		
		
		Image {
				x: 140
				y : 280
				width : 150
				height : 200
				source : "barge.png"
				visible : false
				
				
			}
			
			Rectangle{
			x: 235
			y : 280
			width : 130
			height : 110
			color : "transparent"
			border.width : 2
			border.color : "#00ff00"
			
			Text{
				anchors.horizontalCenter: parent.horizontalCenter
                y: 35
                color: "#D95204"
                text: ("Propeller 1")
                font.pixelSize: 14
				
                font.styleName: "Bold"
                font.weight: Font.Bold
			}
			
            Text {
                id: speed1
                anchors.horizontalCenter: parent.horizontalCenter
                y: 60
                color: "#ffffff"
                text: ("100")
                font.pixelSize: 12
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

			Text {
                id : rpm1
                anchors.horizontalCenter: parent.horizontalCenter
                y: 80
                color: "#ffffff"
                text: ("<font color='white'> 1000 </font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'> 1000 </font>\nRPM")
                font.pixelSize: 12
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            StatusIndicator {
                id: gov1
				anchors.horizontalCenter: parent.horizontalCenter
                y: 5
                width: 24
                height: 31
                active: true
                color: "green"
            }
			
			}


			Rectangle{
			x: 235
			y : 410
			width : 130
			height : 110
			color : "transparent"
			border.width : 2
			border.color : "#00ff00"
			
			Text{
				anchors.horizontalCenter: parent.horizontalCenter
                y: 35
                color: "#D95204"
                text: ("Propeller 2")
                font.pixelSize: 14
				
                font.styleName: "Bold"
                font.weight: Font.Bold
			}
            Text {
                id: speed2
                anchors.horizontalCenter: parent.horizontalCenter
                y: 60
                color: "#ffffff"
                text: ("100")
                font.pixelSize: 12
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            StatusIndicator {
                id: gov2
                anchors.horizontalCenter: parent.horizontalCenter
                y: 5
                width: 24
                height: 31
                active: true
                color: "red"
            }

			Text {
                id : rpm2
                anchors.horizontalCenter: parent.horizontalCenter
                y: 80
                color: "#ffffff"
                text: ("<font color='white'> 1000 </font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'> 1000 </font>\nRPM")
                font.pixelSize: 12
                font.styleName: "Bold"
                font.weight: Font.Bold
            }
			
			}
			
			Rectangle{
			x: 65
			y : 410
			width : 130
			height : 110
			color : "transparent"
			border.width : 2
			border.color : "#00ff00"
			
			Text{
				anchors.horizontalCenter: parent.horizontalCenter
                y: 35
                color: "#D95204"
                text: ("Propeller 3")
                font.pixelSize: 14
				
                font.styleName: "Bold"
                font.weight: Font.Bold
			}
			
            Text {
                id: speed3
                anchors.horizontalCenter: parent.horizontalCenter
                y: 60
                color: "#ffffff"
                text: ("100")
                font.pixelSize: 12
                font.styleName: "Bold"
                font.weight: Font.Bold
            }

            StatusIndicator {
                id: gov3
                anchors.horizontalCenter: parent.horizontalCenter
                y: 5
                width: 24
                height: 31
                active: true
                color: "red"
            
			}


			Text {
                id : rpm3
                anchors.horizontalCenter: parent.horizontalCenter
                y: 80
                color: "#ffffff"
                text: ("<font color='white'> 1000 </font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'> 1000 </font>\nRPM")
                font.pixelSize: 12
                font.styleName: "Bold"
                font.weight: Font.Bold
            }


			}



			Gauge {
				id : power
				x: 185
				y : 280
				width: 10
				height: 240
				value : 66
				tickmarkStepSize: 100
				minorTickmarkCount: 0
				font.pixelSize: 1
				maximumValue : 100
				minimumValue : 0

				style: GaugeStyle {
			
			
			
			valueBar: Rectangle {
				
				color: power_color
				implicitWidth: 15
			}
			
			tickmark: Item {
				implicitWidth: 18
				implicitHeight: 1

				Rectangle {
					visible : false
					color: "#c8c8c8"
					anchors.fill: parent
					anchors.leftMargin: 3
					anchors.rightMargin: 3
				}
			}
		
		}
		
			}

			Rectangle{
				x: 65
				y : 280
				width : 130
				height : 110
				color : "transparent"
				border.width : 2
				border.color : "#00ff00"
				
				Text{
				anchors.horizontalCenter: parent.horizontalCenter
                y: 35
                color: "#D95204"
                text: ("Propeller 4")
                font.pixelSize: 14
				
                font.styleName: "Bold"
                font.weight: Font.Bold
			}
				
				Text {
					id: speed4
					anchors.horizontalCenter: parent.horizontalCenter
					y: 60
					color: "#ffffff"
					text: ("100")
					font.pixelSize: 12
					font.styleName: "Bold"
					font.weight: Font.Bold
				}

				StatusIndicator {
					id: gov4
					anchors.horizontalCenter: parent.horizontalCenter
					y: 5
					width: 24
					height: 31
					active: true
					color: "green"
				}

				Text {
                id : rpm4
                anchors.horizontalCenter: parent.horizontalCenter
                y: 80
                color: "#ffffff"
                text: ("<font color='white'> 1000 </font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'> 1000 </font>\nRPM")
                font.pixelSize: 14
                font.styleName: "Bold"
                font.weight: Font.Bold
            }
			
			}
			
			Rectangle{
			x: 0
			y : 530
			width : 375
			height : 3
			color : "#00ff00"
			visible : true
			
			Text {
					x: 70
					y: 15
					color: "#ffffff"
					text: ("Steering 4 : ")
					font.pixelSize: 12
					font.styleName: "Bold"
					font.weight: Font.Bold
				}
				
			Text {
					id : arrowkiridepan_val
					x: 65
					y: 35
					color: "#ffffff"
					text: "<font color='red'>"+  arrowkiridepan.rotation%360 +"</font>" + "/" + "<font color='white'>"+  arrowkiridepan_target.rotation +"</font>" 
					font.pixelSize: 18
					font.styleName: "Bold"
					font.weight: Font.Bold
				}
			
			
			
			Rectangle{
				id : steering4_status
				x : 150
				y : 5
				width : 50
				height : 50
				color : "transparent"
				border.color : "#00ff00"
				border.width : 2
				radius : width/2
				
				
				Image {
                x : -20
				y : -15
				width : 90
				height : 80
				id: arrowkiridepan_target
                source: "needlewhite.png"
                transformOrigin: Item.Center
				visible :true
				
				rotation: 20
                scale: 1
            }
			
			
			Image {
                x : -20
				y : -15
				width : 90
				height : 80
				visible : true
				id: arrowkiridepan
                source: "needle.png"
                transformOrigin: Item.Center
                rotation: 0
                scale: 1
            }
				
				
				
				
			}
			
			Text {
					x: 70
					y: 80
					color: "#ffffff"
					text: ("Steering 3 : ")
					font.pixelSize: 12
					font.styleName: "Bold"
					font.weight: Font.Bold
				}
			
			Text {
					id : arrowkiribelakang_val
					x: 65
					y: 100
					color: "#ffffff"
					text: "<font color='red'>"+  arrowkiribelakang.rotation%360 +"</font>" + "/" + "<font color='white'>"+  arrowkiribelakang_target.rotation +"</font>" //arrowkiribelakang_target.rotation
					font.pixelSize: 18
					font.styleName: "Bold"
					font.weight: Font.Bold
				}
			
			
			
			
			
			
			
			
			
			Rectangle{
				id:  steering3_status
				x : 150
				y : 65
				width : 50
				height : 50
				color : "transparent"
				border.color : "navy"//"#00ff00"
				border.width : 2
				radius : width/2
				
				
				Image {
				x : -20
				y : -15
				width : 90
				height : 80
                id: arrowkiribelakang_target
				visible : true
				
				source: "needlewhite.png"
                rotation: 155
                scale: 1
            }
				
				Image {
				x : -20
				y : -15
				width : 90
				height : 80
				visible : true
                id: arrowkiribelakang
                source: "needle.png"
                rotation: 0
                scale: 1
            }
				
				
				
			}
			
			Text {
					x: 280
					y: 80
					color: "#ffffff"
					text: ("Steering 2 : ")
					font.pixelSize: 12
					font.styleName: "Bold"
					font.weight: Font.Bold
				}


			Text {
					id : arrowkananbelakang_val
					x: 290
					y: 100
					color: "#ffffff"
					text: "<font color='red'>"+  arrowkananbelakang.rotation%360 +"</font>" + "/" + "<font color='white'>"+  arrowkananbelakang_target.rotation +"</font>" // arrowkananbelakang_target.rotation
					font.pixelSize: 18
					font.styleName: "Bold"
					font.weight: Font.Bold
				}
			
			
			Rectangle{
				id : steering2_status
				x : 220
				y : 65
				width : 50
				height : 50
				color : "transparent"
				border.color : "pink"//"#00ff00"
				border.width : 2
				radius : width/2
			
			 Image {
				x : -20
				y : -15
				width : 90
				height : 80
                id: arrowkananbelakang_target
				visible : true
				
				source: "needlewhite.png"
                rotation: 50
                scale: 1
            }


			
            Image {
				x : -20
				y : -15
				width : 90
				height : 80
                id: arrowkananbelakang
                source: "needle.png"
				visible : true
                rotation: 0
                scale: 1
            }
			
			}
			
			

			
			Text {
					x: 280
					y: 15
					color: "#ffffff"
					text: ("Steering 1 : ")
					font.pixelSize: 12
					font.styleName: "Bold"
					font.weight: Font.Bold
				}
			
			Text {
					id : arrowkanandepan_val
					x: 290
					y: 35
					color: "#ffffff"
					text: "<font color='red'>"+  arrowkanandepan.rotation%360 +"</font>" + "/" + "<font color='white'>"+  arrowkanandepan_target.rotation +"</font>"//arrowkanandepan_target.rotation
					font.pixelSize: 18
					font.styleName: "Bold"
					font.weight: Font.Bold
				}
			
            
			
			
			
			
			Rectangle{
				id : steering1_status
				x : 220
				y : 5
				width : 50
				height : 50
				color : "transparent"
				border.color : "orange"//"#00ff00"
				border.width : 2
				radius : width/2
				
				
				Image {
				x : -20
				y : -15
				width : 90
				height : 80
                id: arrowkanandepan_target
                source: "needlewhite.png"
				visible : true
						 
                rotation: 0
                scale: 1

				}
				
				
				Image {
				x : -20
				y : -15
				width : 90
				height : 80
                id: arrowkanandepan
				visible : true
                source: "needle.png"
                rotation: 0
                scale: 1

				}
			
			
				
				
			}
			
			}
			
			
			
			
			
			
			Image{
			x : 870
			y : 15
			width : 40
			height : 35
			source : "satellite.png"
			
			Text{
				anchors.horizontalCenter: parent.horizontalCenter
				y : 34
				text : "GPS Satellite"
				font.pixelSize : 10
				color : "white"
				
			}


			StatusIndicator{
				id : gps_status
				x : 50
				anchors.verticalCenter: parent.verticalCenter
				height : 30
				width : 30
				color : "red"
				active : true
			}
			}
			
			
			
            
			
			Text {
                id: ship_speed
                x: 430
                y: 22
                width: 32
                height: 19
                color: "#ffffff"
                text: ("0 Kt")
                font.pixelSize: 22
                font.styleName: "Bold"
                font.weight: Font.Bold
            }
			
			Image{
			x : 1100
			y : 20
			width : 100
			height : 35
			source : "syergielogofix.png"
			
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
		
		ListModel{
            id: md_measure
        }


        Plugin {
		   id: mapPlugin
		   name: "osm"

		   //provide the address of the tile server to the plugin
		   PluginParameter {
			  name: "osm.mapping.custom.host"
			  value: "http://localhost/osm/"
		   }

		   /*disable retrieval of the providers information from the remote repository. 
		   If this parameter is not set to true (as shown here), then while offline, 
		   network errors will be generated at run time*/
		   PluginParameter {
			  name: "osm.mapping.providersrepository.disabled"
			  value: true
		   }
		}



        Item {
            id: mapGroup
            x: 360
            y: 63
            width: 940
            height: 660
            property int count : 0
            property real lati : -6.000507
            property real longi : 106.687493
			

			Rectangle {
				width: parent.width
                height: parent.height
				visible :pond_map.checked ? true : false
				color : "#FF7F38"


				Rectangle {
				id : pond_illustration
				anchors.horizontalCenter: parent.horizontalCenter
				anchors.verticalCenter: parent.verticalCenter
				width: 800
                height: 500
				color : "#0487D9"
				border.color : "#993D09"
				border.width : 15


				Rectangle{
					//vessel
					x : 100
					y : 50
					z:999
					width: 100
               		height: 25
					color : "grey"
					border.color : "#373A40"
				}

				MouseArea {
					anchors.fill: parent
					onClicked: { 

					}
				}

	

				}

				TextField{
					x : 90
					y : 30
				}

				TextField{
					x : 700
					y : 600
				}
				
			}


			Map{
                id: map
                x: 0
                y: 0
                width: parent.width
                height: parent.height
                color: "#f9f9f9"
                anchors.rightMargin: 8
                anchors.centerIn: parent;
                anchors.fill: parent
                anchors.verticalCenterOffset: 0
                anchors.horizontalCenterOffset: 0
                anchors.bottomMargin: 0
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.left: parent.left
                anchors.leftMargin: 0
                zoomLevel : 1000.03
				minimumZoomLevel: 10.03
				maximumZoomLevel: 1000.4
                copyrightsVisible: true
                antialiasing: true
                maximumTilt: 89.3
                plugin: mapPlugin
                activeMapType: supportedMapTypes[0]

                //center: QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text)
                //center: QtPositioning.coordinate(1.0204327129524284 , 103.92695632739532)
				center: QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text)
				gesture.enabled: true
                gesture.acceptedGestures: MapGestureArea.PinchGesture | MapGestureArea.PanGesture



                visible :pond_map.checked ? false : true
				
					Repeater {
					model: allPolygons

					MapQuickItem {
						z: 999  // agar di atas polygon
						coordinate: QtPositioning.coordinate(modelData.center.latitude, modelData.center.longitude)
						anchorPoint.x: 30
						anchorPoint.y: 10
						sourceItem: Rectangle {
							color: "white"
							border.color: "black"
							border.width: 1
							radius: 4
							opacity: 0.7
							width: textItem.paintedWidth + 10
							height: textItem.paintedHeight + 6

							Text {
								id: textItem
								anchors.centerIn: parent
								text: modelData.value.toFixed(2) + " m"
								color: "black"
								font.bold: true
								font.pointSize: 10
							}
						}
					}
				}

					
				
				
				
				Repeater {
            model: allPolygons

            MapPolygon {
                path: modelData.points
                border.width: 1
                border.color: "black"

                // Warna biru berdasarkan kedalaman: makin dalam, makin gelap
                //color: Qt.rgba(0, 0, 1, Math.min(1, modelData.value / 100)) // transparansi = 0~1
				 opacity: 0.5

				color: modelData.value < 1                 ? "#D98014" :        // Dangkal < 1m
				   modelData.value > 1 && modelData.value < 5   ? "#F2BB13" :  // 1-5m
				   modelData.value >= 5 && modelData.value < 10 ? "#16B4F2" :  // 5-10m
				   modelData.value >= 10 && modelData.value < 25 ? "#117CD9" : // 10-25m
																   "transparent"   // >=25m
						MapQuickItem {
							coordinate: modelData.center
							anchorPoint.x: 30
							anchorPoint.y: 10
							sourceItem: Rectangle {
								color: "white"
								opacity: 0.7
								radius: 4
								width: textItem.width + 10
								height: textItem.height + 6

								Text {
									id: textItem
									anchors.centerIn: parent
									text: modelData.value + " m"
									color: "black"
									font.bold: true
									font.pointSize: 10
								}
							}
						}
					}
				}
					
				
			
			Rectangle{
				x:200
				y:430
				z : 999
				width : 200
				height : 50
				color : "white"
				border.color: "black"
				border.width: 3
				
				Rectangle{
				x:5
				y:20
				width : 35
				height : 6
				color : "yellow"
				rotation : -45
				}
				
				
				Text {
				id : depth_est
                x:40
                y:15
                width: 95
                height: 19
                color: "black"
                text: "depth est : 0m"
                font.pixelSize: 15
                font.styleName: "Bold"
                
				}
				
				
			}

			
			
			Text{
				id : lat_target
				text : "5"//backend.lat_target()
				visible : false
				
			}
			
			Text{
				id : long_target
				text : "3"//backend.long_target()
				visible : false
				
			}
			
			
			

                

				Linemeasure{
                    id: li_measure
                }


                Line1{
                    id: li1
                }

                Line2{
                    id: li2
                }

				Line3{
                    id: li3
                }
				
				
				Line_cilacap1{
						id : cilacap1
				
				}
				
				
				Line_cilacap2{
						id : cilacap2
				
				}


				Line{
                    id: li
                }

                

                Line_rpl1{
                    id:rpl_ondong_manado
                }

				Line_rpl2{
                    id:rpl_ondong_tahuna

                }

                Line5{
                    id:sanana_taliabu
                }
				
				
               Line6{
                    id:route
                }
				
				
                Line7{
                    id:circleondong_tahuna
                }


                Line8{
                    id:actaliabu_sanana
                }

				
				// selayar lingga
				MapCircle { 
                    center {
                        latitude: -0.286233332999927
                        longitude: 104.482733333 //#1
                    }
                    radius: 50
                    color: '#46a2da'
                    border.color: "#190a33"
                    border.width: 3
                }
				
				
				MapCircle { 
                    center {
                        latitude: -0.285329787999956
                        longitude: 104.49097057 //#2
                    }
                    radius: 50
                    color: '#46a2da'
                    border.color: "#190a33"
                    border.width: 3
                }
				
				
				MapCircle { 
                    center {
                        latitude: -0.286317332999943
                        longitude: 104.502558028 //#3
                    }
                    radius: 50
                    color: '#46a2da'
                    border.color: "#190a33"
                    border.width: 3
                }
				
				MapCircle { 
                    center {
                        latitude:-0.28126231799996
                        longitude: 104.512625181 //#4
                    }
                    radius: 50
                    color: '#46a2da'
                    border.color: "#190a33"
                    border.width: 3
                }
				
				
				MapCircle { 
                    center {
                        latitude:-0.276440679999951
                        longitude: 104.514920141 //#5
                    }
                    radius: 50
                    color: '#46a2da'
                    border.color: "#190a33"
                    border.width: 3
                }
				
				MapCircle { 
                    center {
                        latitude:-0.273599999999931
                        longitude: 104.51545 //#6
                    }
                    radius: 50
                    color: '#46a2da'
                    border.color: "#190a33"
                    border.width: 3
                }

				// dabo selayar
				
				MapCircle {
					center {
						latitude: -0.276440679999951
						longitude: 104.514920141 //#5
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.341294
						longitude: 104.462844
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.340964
						longitude: 104.462765
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.339872
						longitude: 104.462503
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.338025
						longitude: 104.462061
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.335381
						longitude: 104.461428
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.33275
						longitude: 104.460797
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.330567
						longitude: 104.460275
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.328868
						longitude: 104.459868
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}

				MapCircle {
					center {
						latitude: -0.328686
						longitude: 104.459825
					}
					radius: 50
					color: '#46a2da'
					border {
						color: "#190a33"
						width: 3
					}
				}


				//batam buluh
				MapCircle {
					center {
						latitude: 1.02601
						longitude: 103.92565
					}
					radius: 50
					color: "#46a2da"
					border {
						color: "#190a33"
						width: 3
					}
				}
				MapCircle {
					center {
						latitude: 1.02573
						longitude: 103.92547
					}
					radius: 50
					color: "#46a2da"
					border {
						color: "#190a33"
						width: 3
					}
				}
				MapCircle {
					center {
						latitude: 1.02182
						longitude: 103.92303 
					}
					radius: 50
					color: "#46a2da"
					border {
						color: "#190a33"
						width: 3
					}
				}
				MapCircle {
					center {
						latitude: 1.01952
						longitude: 103.92350
					}
					radius: 50
					color: "#46a2da"
					border {
						color: "#190a33"
						width: 3
					}
				}
				MapCircle {
					center {
						latitude: 1.01757
						longitude: 103.92500
					}
					radius: 50
					color: "#46a2da"
					border {
						color: "#190a33"
						width: 3
					}
				}
				
				MapCircle {
					center {
						latitude: 1.01833
						longitude: 103.92597
					}
					radius: 50
					color: "#46a2da"
					border {
						color: "#190a33"
						width: 3
					}
				}


				


                Timer {
					

                    function updateloc() {
					
                     
					
					if (li1.pathLength() < 500){
                                var text = md1.count + 1;

                                md1.append({"coords": QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text),
                                               "title": text})
											   
					}

					
                       if (tracking_line.checked == true){
							var text = md1.count + 1;

                            md1.append({"coords": QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text),
                                           "title": text})
                            li1.addCoordinate(QtPositioning.coordinate(latitude_position_value.text, longitude_position_value.text))
                        }

                        
						if (tracking_line.checked == false){
                            for (var index = li1.pathLength(); index >= 0; index--)
                            {
                                li1.removeCoordinate([index]);
                            }
												
							
                        }
						
					
					
                    
					
					}
                    interval: 1000; running: true; repeat: true
                    onTriggered: {
                        updateloc()
                    }
                }





                Timer {


                    function updateloc2() {
						
					
					}
					
                    interval: 2000; running: true; repeat: true
                    onTriggered: {
                        updateloc2()
                    }
                }





		MapItemView{
            model: md
            delegate: Marker{
                text: title
                coordinate: QtPositioning.coordinate(coords.latitude, coords.longitude)
            }
        }

		MapItemView{
            model: md2
            delegate: Marker{
                text: title
                coordinate: QtPositioning.coordinate(coords.latitude, coords.longitude)
            }
        }

		MapItemView{
            model: md_measure
            delegate: Marker{
                text: title
                coordinate: QtPositioning.coordinate(coords.latitude, coords.longitude)
            }
        }

        Line{
            id: lili
        }

				
                //menampilkan koordinat sesuai mouse
                MouseArea {
					
                    hoverEnabled: true
                    property var coordinate: map.toCoordinate(Qt.point(mouseX, mouseY))
                    x: 0
                    y: 0
                    width: parent.width//780
                    height: parent.height//331
                    //anchors.rightMargin: -30
                    //anchors.leftMargin: 19
                    //anchors.fill: parent
					acceptedButtons: Qt.LeftButton | Qt.RightButton

					Label
                    {
                        x: parent.mouseX - width
                        y: parent.mouseY - height - 5
                        //text: "lat: %4; lon:%10".arg(parent.coordinate.latitude).arg(parent.coordinate.longitude)
                        text: "Lat : " + (parent.coordinate.latitude).toFixed(6) + " Long :" + (parent.coordinate.longitude).toFixed(6)      
						color:"navy"

                    }
					
					
					Text{
						id : lat_mouse
						x: parent.mouseX - width
                        y: parent.mouseY - height - 5
						text: (parent.coordinate.latitude).toFixed(6)
						color : "red"
						visible : false
						
					}
					
					Text{
						id : long_mouse
						x: parent.mouseX - width
                        y: parent.mouseY - height - 5
						text: (parent.coordinate.longitude).toFixed(6)
						color : "red"
						visible : false
						
					}
					
                    property var panjanglintasan: li.pathLength()
                    property var path: li.path
					
					
					
                    onDoubleClicked: {
						if (autopilot_button.checked == true){
							
							var crd = map.toCoordinate(Qt.point(mouseX, mouseY))
							console.log("autopilot_route")
							backend.rpl_point(crd.latitude, crd.longitude)
							
							markerModel.append({ "latitude":lat_mouse.text, "longitude": long_mouse.text})
                            var text = md.count + 1;
                            md.append({"coords": coordinate, "title": text})
                            li.addCoordinate(coordinate)
							
						}

						if (ruler.checked == true){
							var crd = map.toCoordinate(Qt.point(mouseX, mouseY))
							

							//markerModel.append({ "latitude":crd.latitude, "longitude": crd.longitude})
							md_measure.append({"coords": coordinate, "title": ""})
							
							ruler_count = ruler_count + 1
							
							if(ruler_count < 2){
								lat1 = crd.latitude
								long1 = crd.longitude
								ruler_measurement = 0

							} else {
								lat2 = crd.latitude
								long2 = crd.longitude

								ruler_measurement += meter_conversion(lat1, long1, lat2, long2)
								console.log(lat1, long1, lat2, long2, ruler_measurement)

								//lat1 = lat2
								//lat1 = lat2
							}

							
							li_measure.addCoordinate(coordinate)
							console.log(ruler_count)
							
						}

                    }

				Button{
				id : line1
				x: 290
				y : 10
				width : 50
				height : 45
				text : "1"
				checkable : true
				
				onClicked:{
					//markerModel.clear()
					upload_csv()
					backend.estimate_rpl(1)
					line2.checked = false
					//markerModel.append({ "latitude":lat_mouse.text, "longitude": long_mouse.text})
				}
				
				}
				
				Button{
				id : line2
				x: 290
				y : 60
				width : 50
				height : 45
				text : "2"
				checkable : true
				
				onClicked:{
					upload_csv()
					backend.estimate_rpl(2)
					line1.checked = false
					}
				}


				Button{
				id : lock_position
				x: 350
				y : 10
				width : 50
				height : 45
				text : ""
				checkable : true

				
				Image{
					anchors.centerIn: parent
					width : parent.width - 10
					height : parent.height - 10
					source : "lock.png"
				}

				Rectangle{
					width : parent.width
					height : parent.height
					border.width : 3
					border.color : "black"
					color : "transparent"
				}

				


				onClicked:{

					if (lock_position.checked == true){
						backend.station_keeping("on", latitude_position_value.text, longitude_position_value.text)
					} else {
						backend.station_keeping("off", latitude_position_value.text, longitude_position_value.text)
					}
					
					
				}
				
			}
				
				

				Button{
				id : control_auto
				x: 440
				y : 10
				width : 50
				height : 45
				text : ""
				checkable : true

				
				Image{
					anchors.centerIn: parent
					width : parent.width - 10
					height : parent.height - 10
					source : "robot.svg"
				}

				Rectangle{
					width : parent.width
					height : parent.height
					border.width : 3
					border.color : "black"
					color : "transparent"
				}

				


				onClicked:{

					if (control_auto.checked == true){
						backend.user_control("auto")
						line_ongoing.visible = true
					} else {
						backend.user_control("manual")
						line_ongoing.visible = false
					}
					
					
				}
				
			}
					
				Button{
				x: 550
				y : 0
				z : 999
				text: "clear line target"
				visible : true


				onClicked:{
					md.remove(md.count - 1);
					var index = li.pathLength() 
					li.removeCoordinate([index] - 1);
					backend.remove("front")
	
				}
				
			}


			Button{
				x: 550
				y : 50
				text: "Clear Line Back"
				visible : true
				onClicked:{
					backend.remove("back")							
                    }
			}


			Button{
				id : heading_lock
				x: 550
				y : 100
				text: "Heading Lock"
				visible : true
				checkable : true
				onClicked:{
					if (checked){
						backend.heading_first("yes")
						console.log("head")
						
					} else {
						backend.heading_first("no")
						console.log("free")
						//slider.visible = false
					}
					//backend.remove("back")							
                    }
			}
						
						



                }




				MapPolyline {
					id : line_ongoing
					line.width: 3
					line.color: 'red'
					visible : false // (rpl_lat && rpl_lat.length > 0 && rpl_long && rpl_long.length > 0)
					path: [
						 
						{ latitude: latitude_position_value.text, longitude: longitude_position_value.text },
						//{ latitude: rpl_lat[0], longitude: rpl_long[0]}
						{ latitude: rpl_lat && rpl_lat.length > 0 ? rpl_lat[0] : latitude_position_value.text,
          				longitude: rpl_long && rpl_long.length > 0 ? rpl_long[0] : longitude_position_value.text }
					
					]
				 }


                //Kapal
                MapQuickItem{
                    id : marker
					z : 999
                    sourceItem : Image{
                        id: imagenavigasi
                        width: 33
                        height: 37
						
                        //transformOrigin: Item.Center
                        source:"vessel.png"
						//source:"segitiga.png"
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
                    //coordinate: QtPositioning.coordinate(latitude_destination.text, longitude_destination.text)
                    anchorPoint.x : 15
                    anchorPoint.y : 14
                    //anchorPoint.x : parent
                    //anchorPoint.y : parent

                }
				


                Rectangle {
                    id: rectangle
                    x: 840
                    y: 508
                    width: 92
                    height: 47
                    color: "#a18cd1"
                    radius: 10
					visible : false
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
                            md.clear()
                            for (var index = li.pathLength(); index >= 0; index--)
                            {
                                
                                li.removeCoordinate([index]);
                                li1.removeCoordinate([index]);
                                
                            }
                        }
                    }
                }



                MapQuickItem{
                    id : bouy

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



                MapItemView {
                    id: mivMarker
                    model: ListModel {
                        id: markerModel
                    }
                    delegate: Component {
                        MapQuickItem {
                            coordinate: QtPositioning.coordinate(latitude, longitude)
                            property real slideIn: 0
                        }
                    } 
                }
            }	
        }


        Button {
            id: navionic
            x: 1264
            y: 110
            width: 34
            height: 31
            checkable: true
            checked: false
			visible : false
            Image {
                id: wkwk1
                anchors.fill: parent
                source: "navionic.png"
            }
        }
    }

	
			
		
		Rectangle{
			x: 350
            y: 63
            width: 948
            height: 660
			color : "transparent"
			border.color : "#00ff00"
			border.width : 3

		 Button {
            id:tracking_line
            x: 550
            y: 150
            width : 70
			height  :70
            checkable: true
            checked: false
			text : ""

			Image{
				anchors.centerIn: parent
				width : parent.width - 20
				height : parent.height - 20
				source : "save loc.png"
        		}

			Rectangle{
				width : parent.width
				height : parent.height
				border.width : 3
				border.color : "black"
				color : "transparent"
			}

		 }
		
		
		Text {
			id : line_length
			x : 10
			y : 10
			text : "Line Length : 0 m"
			font.pixelSize : 15
			color : "blue"
			font.family: "Helvetica"
			font.bold : true
		}
		
		Text {
			id : navigation_mode
			x : 10
			y : 60
			text : "NAV MODE: "
			font.pixelSize : 15
			color : "blue"
			font.family: "Helvetica"
			font.bold : true
		}


		Text {
			id : control_style
			x : 10
			y : 90
			text : "manual"
			font.pixelSize : 15
			color : "blue"
			font.family: "Helvetica"
			font.bold : true
		}


		Text {
				id : position_error
                x : 10
                y: 130
               
                text: ("position error : ")
				font.pixelSize : 15
				color : "blue"
				font.family: "Helvetica"
				font.bold : true
                
            }
			
			Text {
				id : dir_error
                x : 10
                y: 160
                text: ("DIR ERROR : ")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }

			Text {
				id : heading_error
                x : 10
                y: 180
                text: ("HEADING ERROR : ")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }


			Text {
				id : heading_speed
                x : 10
                y: 200
                text: ("heading speed : ")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }

			Text {
				id : drive_mode
                x : 10
                y: 230
                text: ("drive mode : ")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }


			Rectangle {
                x : 10
                y: 270
                width : 150
				height : 200
				color : "transparent"
				border.color : "blue"
				border.width : 2

				Text {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 5
                text: ("constanta")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }

				Text {
				id : control_prop
                x : 5
                y: 30
                text: ("ṅ : ")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }

	
            }


			Rectangle {
                x : 160
                y: 270
                width : 150
				height : 200
				color : "transparent"
				border.color : "blue"
				border.width : 2
				visible : false

				Text {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 5
                text: ("ship dynamics")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }


			Text {
				id : dynamic_prop
                x : 5
                y: 30
                text: ("v : \nV̇:\n τ:")
                color : "blue"
				font.pixelSize : 15
				font.family: "Helvetica"
				font.bold : true
            }


			}

			//route target
			Button {
			id : autopilot_button
            x: 550
            y: 250
            text : ""
			width : 70
			height : 70
            checkable: true
            checked: false

			Image{
				anchors.centerIn: parent
				width : parent.width - 20
				height : parent.height - 20
				source : "route.svg"
			}

			Rectangle{
				width : parent.width
				height : parent.height
				border.width : 3
				border.color : "black"
				color : "transparent"
			}
			


			onClicked:{
				
				
			}
			
			}

			Button {
            id: pond_map
            x: 550
            y: 350
            text : ""
			width : 70
			height  :70
            checkable: true
            checked: false


			Rectangle{
				width : parent.width
				height : parent.height
				border.width : 3
				border.color : "black"
				color : "transparent"
			}


			Image{
				anchors.centerIn: parent
				width : parent.width - 20
				height : parent.height - 20
				source : "lake.png"
			}

		}
			
			

		
    


		Button {
            id: camera
            x: 550
            y: 450
            text : ""
			width : 70
			height  :70
            checkable: true
            checked: false
			
			Rectangle{
				width : parent.width
				height : parent.height
				border.width : 3
				border.color : "black"
				color : "transparent"
			}


			Image{
				anchors.centerIn: parent
				width : parent.width - 20
				height : parent.height - 20
				source : "camera.svg"
			}

		}
		
		
		Button {
            x: 100
            y: 500
            text : ""
			width : 70
			height  :70
            checkable: false
            checked: false

			Rectangle{
				width : parent.width
				height : parent.height
				border.width : 3
				border.color : "black"
				color : "transparent"
			}


			Image{
				anchors.centerIn: parent
				width : parent.width - 20
				height : parent.height - 20
				source : "eraser.svg"
			}

			onClicked:{
				for (var index = li_measure.pathLength(); index >= 0; index--)
                            {
                                li_measure.removeCoordinate([index]);
                            }

					ruler_count = 0
					md_measure.clear()
					ruler_measurement = 0
			}

		}
		

		Rectangle { 
			id : joystick_color
            x: 370
            y: 560
			width : 70
			height  :70
			color : "#2BC088" //#F7286E
			border.color : "#2A0B2F"
			border.width : 3

			Text{
				x : 80
				y : -25
				text : "JOYSTICK"
				font.pixelSize: 17
				color : "#0C2D57" 
				
			}

			Image{
				anchors.centerIn: parent
				width : parent.width - 15
				height : parent.height - 15
				source : "joystick.png"
			}

		}


		Rectangle { 
			id : joystick2_color
            x: 540
            y: 560
			width : 70
			height  :70
			color : "#F7286E" //#F7286E
			border.color : "#2A0B2F"
			border.width : 3


			Image{
				anchors.centerIn: parent
				width : parent.width - 15
				height : parent.height - 15
				source : "joystick 2.png"
			}


		}



		CustomSwitch{
		id: joystick_selector
		x:450
		y:570
		backgroundHeight: 25
		backgroundWidth: 75
		visible : false
		onSwitched:{
			
			if(on == true){

				
				}
			else{

			}

			
			}
		
		}


		Button {
            id: ruler
            x: 20
            y: 500
            text : ""
			width : 70
			height  :70
            checkable: true
            checked: false

			Text{
				x : 0
				y : -25
				text : "RULER MEASUREMENT"
				font.pixelSize: 17
				color : "#0C2D57"
				
			}
			
			Image{

				anchors.centerIn: parent
				width : parent.width - 20
				height : parent.height - 20
				source : "ruler.svg"
			}

			Rectangle{
				width : parent.width
				height : parent.height
				border.width : 3
				border.color : "black"
				color : "transparent"
			}


			onClicked:{
				if(ruler.checked == false){
					
				}
			}

		}
		

		Rectangle{
			x: 500
            y: 350
			visible : camera.checked

			width : 420
			height  :300
			border.width : 3
			border.color : "#00ff00"


			Rectangle{
				id : camera_frame
				width : parent.width - 6
				height : parent.height - 6 
				anchors.horizontalCenter: parent.horizontalCenter
				anchors.verticalCenter: parent.verticalCenter

				CVItem  {
				id: imageWriter
				anchors.fill: parent
				image: capture.image
				}
	
	

				CVCapture{
					id: capture
					index: 0
					filters: []//[max_rgb_filter, gray_filter]
					Component.onCompleted: capture.stop()
				}

			}


			Button{
				id : reconnect_button
				anchors.horizontalCenter: parent.horizontalCenter
				y: 250
				text:"Camera Switch"
				checkable : true
				
				onClicked:{
					if (reconnect_button.checked == true){
						capture.start()
						camera_frame.visible = true
					} else {
						capture.stop()
						camera_frame.visible = false
					}
				}

			}


		}
		
		
		
		}




	Rectangle{
		x : 733
		y : 600
		width : 540
		height : 130
		color : "#0C2D57"
		border.color : "#00ff00"
		border.width : 2
		visible : false
		 Image {
				x : 5
				y : 5
                width : 120
				height :120
                source: "itb.png"
            }
			
			Text {
					x : 150
					y: 20
					width : 400
					wrapMode: Text.WordWrap  
					horizontalAlignment: Text.AlignJustify
					color: "#ffffff"
					text: "23223303\nMUHAMMAD HUSNI MUTTAQIN\nPOSTGRADUATE FINAL THESIS\nCONTROL ENGINEERING AND INTELLIGENCE SYSTEM\nINSTITUT TEKNOLOGI BANDUNG"
					font.pixelSize: 14
					font.styleName: "Bold"
					font.weight: Font.Bold
					
				}
		
		
	}


	Button{
		id : ship_parameter
		x : 400
		y : 650
		text : "ship parameter"

		Rectangle{
				width : parent.width
				height : parent.height
				color : ship_parameter.checked ? "blue" : "gray"
			}


		onClicked:{
			wnd_ship_parameter.visible = true
		}
	}



	Rectangle{
		x : 550
		y : 550
		width : 150
		height : 150
		radius : width/2
		color : "#8DCBF2"
		border.color : "#192655"
		border.width : 2


		Rectangle{
		id : wind_attack
		width : parent.width
		height : parent.height
		radius : width/2
		color : "transparent"
		border.color : "green"
		border.width : 4

		Rectangle {
			x : parent.width/2 - 2
			y : 0
			width : 5
			height : 30
			color : "blue"
		}


		}


		


		Rectangle{
		id : radar
		width : parent.width
		height : parent.height
		color : "transparent"

		
		rotation : (radar_debug.value)-180
		
		



		Rectangle{
			id : radar_gauge
			x : parent.width/2 - 3
			y : parent.width/2
			width : 6
			height : 75
			color : "#192655"
			visible : true
			

			Image{
				x: -10
				y : parent.height - 10
				width : 25
				height : 25
				source : "cross_orange.png"

			}
		}


		}


		Image{
			anchors.centerIn: parent
			width : 30
			height : 30
			source : "navigasi.png"
		}

	}

    
	
	

}



Window {
        id: wnd_ship_parameter
        visible: false
		color : "#0C2D57"
		title:"Ship Parameter"
		width: 800
		height: 600
		maximumWidth : 800
		minimumWidth : 800

		maximumHeight : 600
		minimumHeight : 600
		

		Button{
			id : ship_type
			x : 22
			y: 30
			text : "Ship Type"
			checked : true
			checkable : true

			Rectangle{
				width : parent.width
				height : parent.height
				color : ship_type.checked ? "blue" : "gray"
			}
			onClicked:{
				if (ship_type.checked == true){
					hardware_setting.checked = false
					control_type.checked = false
					rpl.checked = false

					ship_type_page.visible = true
					hardware_setting_page.visible = false
					control_type_page.visible = false
					navigation_page.visible = false
				}
			}

		}

		Button{
			id : hardware_setting
			x : 152
			y: 30
			text : "Hardware_setting"
			checked : false
			checkable : true

			Rectangle{
				width : parent.width
				height : parent.height
				color : hardware_setting.checked ? "blue" : "gray"
			}

			onClicked:{
			if (hardware_setting.checked == true){
					ship_type.checked = false
					control_type.checked = false
					rpl.checked = false
					

					ship_type_page.visible = false
					hardware_setting_page.visible = true
					control_type_page.visible = false
					navigation_page.visible = false
				}
			}
		}

		Button{
			id : control_type
			x : 284
			y: 30
			text : "Control Type"
			checked : false
			checkable : true

			Rectangle{
				width : parent.width
				height : parent.height
				color : control_type.checked ? "blue" : "gray"
			}

			onClicked:{
			if (control_type.checked == true){
					ship_type.checked = false
					hardware_setting.checked = false
					rpl.checked = false
					console.log("executed")

					ship_type_page.visible = false
					hardware_setting_page.visible = false
					control_type_page.visible = true
					navigation_page.visible = false
				}
			}
		}

		Button{
			id : rpl
			x : 416
			y: 30
			text : "Navigation"
			checked : false
			checkable : true

			Rectangle{
				width : parent.width
				height : parent.height
				color : rpl.checked ? "blue" : "gray"
			}

			onClicked:{
			if (rpl.checked == true){
					ship_type.checked = false
					hardware_setting.checked = false
					control_type.checked = false
					console.log("executed")

					ship_type_page.visible = false
					hardware_setting_page.visible = false
					control_type_page.visible = false
					navigation_page.visible = true
				}
			}
		}

		Rectangle{
			id : ship_type_page
			anchors.centerIn: parent
			height: 450
			width : 750
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"

			
		

			Image{
			x : 10
			height: 250
			width : 500
			source : "ship_top.png"
			anchors.verticalCenter: parent.verticalCenter
			visible : true

		}




		Text{
			//anchors.horizontalCenter: parent.horizontalCenter
			x : 20
			y : 420
			text : "Length : "
			font.pixelSize : 22
			color : "#00ff00"
			font.family: "Helvetica"
		}

			TextInput{
			x : 120
			y : 420
			text : "76"
			font.pixelSize : 22
			color : "#ffff33"
			font.family: "Helvetica"
		}

		Text{
			//anchors.horizontalCenter: parent.horizontalCenter
			x : 180
			y : 420
			text : "Breath : "
			font.pixelSize : 22
			color : "#00ff00"
			font.family: "Helvetica"
		}

		TextInput{
			x : 260
			y : 420
			text : "21"
			font.pixelSize : 22
			color : "#ffff33"
			font.family: "Helvetica"
		}


		Text{
			//anchors.horizontalCenter: parent.horizontalCenter
			x : 320
			y : 420
			text : "Tonnage : "
			font.pixelSize : 22
			color : "#00ff00"
			font.family: "Helvetica"
		}

		TextInput{
			x : 420
			y : 420
			text : "4700"
			font.pixelSize : 22
			color : "#ffff33"
			font.family: "Helvetica"
		}


		Text{
			//anchors.horizontalCenter: parent.horizontalCenter
			x : 510
			y : 420
			text : "Draft : "
			font.pixelSize : 22
			color : "#00ff00"
			font.family: "Helvetica"
		}

		TextInput{
			x : 580
			y : 420
			text : "4"
			font.pixelSize : 22
			color : "#ffff33"
			font.family: "Helvetica"
		}




		Button{
			x : 600
			y : 10
			text : "save"
		}

		Rectangle {
		id : propeller1_position
        x: 389
		y: 354
        width: 50
		height: 50
        color: "red"
		radius : height/2

        Drag.active: dragArea1.drag.active
        Drag.hotSpot.x: 0
        Drag.hotSpot.y: 0

		Text {
			id : propeller1_properties
			x : 70
			y : 0
			text : ""
			font.pixelSize : 13
			color : "#00ff00"
			font.family: "Helvetica"
			font.bold : true
		}

        MouseArea {
            id: dragArea1
            anchors.fill: parent
			drag.axis: Drag.XAxis
            drag.target: parent
			onClicked:{
				console.log("clicked")
			}
        }
    	
		}


		Rectangle {
		id : propeller2_position
        x: 80
		y: 354
        width: 50
		height: 50
        color: "red"
		radius : height/2

        Drag.active: dragArea2.drag.active
        Drag.hotSpot.x: 0
        Drag.hotSpot.y: 0


		Text {
			id : propeller2_properties
			x : 70
			y : 0
			text : ""
			font.pixelSize : 13
			color : "#00ff00"
			font.family: "Helvetica"
			font.bold : true
		}

        MouseArea {
            id: dragArea2
            anchors.fill: parent
			drag.axis: Drag.XAxis
            drag.target: parent
        }
    	
		}
	
		Rectangle {
		id : propeller3_position
        x: 80
		y: 45
        width: 50
		height: 50
        color: "red"
		radius : height/2

        Drag.active: dragArea3.drag.active
        Drag.hotSpot.x: 0
        Drag.hotSpot.y: 0

		Text {
			id : propeller3_properties
			x : 70
			y : 0
			text : ""
			font.pixelSize : 13
			color : "#00ff00"
			font.family: "Helvetica"
			font.bold : true
		}

        MouseArea {
            id: dragArea3
            anchors.fill: parent
			drag.axis: Drag.XAxis
            drag.target: parent
        }
    	
		}


		Rectangle {
		id : propeller4_position
        x: 389
		y: 45
        width: 50
		height: 50
        color: "red"
		radius : height/2

        Drag.active: dragArea4.drag.active
        Drag.hotSpot.x: 0
        Drag.hotSpot.y: 0

		Text {
			id : propeller4_properties
			x : 70
			y : 0
			text : ""
			font.pixelSize : 13
			color : "#00ff00"
			font.family: "Helvetica"
			font.bold : true
		}

        MouseArea {
            id: dragArea4
            anchors.fill: parent
			drag.axis: Drag.XAxis
            drag.target: parent
        }
    	
		}

		Image{
			id : cog
			x : 197
			y : 206
			width : 50
			height : 50
			source : "CoG.png"

			Drag.active: dragArea5.drag.active
			Drag.hotSpot.x: 0
			Drag.hotSpot.y: 0
			
			Text {
			id : cog_properties
			x : 70
			y : 0
			text : ""
			font.pixelSize : 13
			color : "#00ff00"
			font.family: "Helvetica"
			font.bold : true
		}


			MouseArea {
            id: dragArea5
            anchors.fill: parent

            drag.target: parent
        }


		}


		Text{
			//anchors.horizontalCenter: parent.horizontalCenter
			x : 550
			y : 130
			text : "Ship Type : "
			font.pixelSize : 22
			color : "#00ff00"
			font.family: "Helvetica"
		}

		Button{
			id : barge_select
			x : 550
			y : 200
			text : "BARGE"
			checked : true
			checkable : true
			onClicked: {
				lct_select.checked = false
				tug_select.checked = false
			}
		}

		Button{
			id : lct_select
			x : 550
			y : 250
			text : "LCT"
			checked : false
			checkable : true
			onClicked: {
				barge_select.checked = false
				tug_select.checked = false
			}
		}

		Button{
			id : tug_select
			x : 550
			y : 300
			text : "Tug"
			checked : false
			checkable : true
			onClicked: {
				lct_select.checked = false
				barge_select.checked = false
			}
		}


		}


		Rectangle{
			id : hardware_setting_page
			anchors.centerIn: parent
			height: 450
			width : 750
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"
			visible : false

			




		}

		Rectangle{
			id : control_type_page
			anchors.centerIn: parent
			height: 450
			width : 750
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"
			visible : false


			Item {
        
        anchors.fill: parent
        width:root.width
        height: root.height
        
		
		ScrollView {
            
            anchors.fill:parent
		
			
			
            
		style: ScrollViewStyle {
			handle: Rectangle {
			x: 0
            implicitWidth: 10
            implicitHeight: 30
            color: "red"
			
        }
		
		minimumHandleLength : 10
		
        scrollBarBackground: Rectangle {
            implicitWidth: 10
            implicitHeight: 30
            color: "transparent"
        }
        decrementControl: Rectangle {
            implicitWidth: 0
            implicitHeight: 0
            color: "transparent"
        }
        incrementControl: Rectangle {
            implicitWidth: 0
            implicitHeight: 0
            color: "transparent"
        }
    }
			
            Column{
                width:parent.width
                spacing:1
				Rectangle{
					
					width: control_type_page.width
					height: 50
					color: "#0C2D57"
					border.width : 2
					border.color : "#00ff00"


					 CheckBox {
						id: scheme1
						checked: true
						
						Text {
								x : 50
								y : 10
								text: "Scheme 1"
								color: "white"  // Mengubah warna teks menjadi putih
								font.pixelSize: 16  // Ukuran font 12
							}
						

						onClicked: {
							if (scheme1.checked == true){
								backend.fsm_scheme("scheme1")
								scheme2.checked = false
							}
							
						}
					}

				}
				Rectangle{
					
					width: control_type_page.width
					height: 300
					color: "#0C2D57"
					border.width : 2
					border.color : "#00ff00"

					GridLayout {
					id: grid_gain1
					anchors.fill: parent
					columns: 2
					rows: 4 // Secara implisit ditentukan oleh jumlah TextField yang dibuat

					Repeater {
						model: 2 * 4 // Total 36 TextField (9 rows x 4 columns)
						delegate: TextField {
							//text : "0.5"
							Layout.fillWidth: true
							Layout.fillHeight: true
							
							placeholderText: "zone :  " + (Math.floor(index / grid_gain1.columns) + 1) +
											", " + ((index % grid_gain1.columns) === 0 ? "x_gain" :
											(index % grid_gain1.columns) === 1 ? "y_gain" :
											(index % grid_gain1.columns) === 2 ? "yaw_pos_gain" :
											"yaw_neg_gain")
							
							// Track the text of each TextField
							onTextChanged: {
								fsm_data1[index] = text
							}
						}
					}
				}

				}

                Rectangle{
					
					width: control_type_page.width
					height: 50
					color: "#0C2D57"
					border.width : 2
					border.color : "#00ff00"


					CheckBox {
						id: scheme2
						checked: false
						
						Text {
								x : 50
								y : 10
								text: "Scheme 2"
								color: "white"  // Mengubah warna teks menjadi putih
								font.pixelSize: 16  // Ukuran font 12
							}
						

						onClicked: {
							if (scheme2.checked == true){
								backend.fsm_scheme("scheme2")
								scheme1.checked = false
							}
							
						}
					}

				}
				Rectangle{
					
					width: control_type_page.width
					height: 600
					color: "#0C2D57"
					border.width : 2
					border.color : "#00ff00"

				
            GridLayout {
                id: gridLayout
                anchors.fill: parent
                columns: 4
                rows: 9 // Secara implisit ditentukan oleh jumlah TextField yang dibuat

                Repeater {
                    model: 9 * 4 // Total 36 TextField (9 rows x 4 columns)
                    delegate: TextField {
						//text : "0.5"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
						
						placeholderText: "zone :  " + (Math.floor(index / gridLayout.columns) + 1) +
                                         ", " + ((index % gridLayout.columns) === 0 ? "x_gain" :
										(index % gridLayout.columns) === 1 ? "y_gain" :
										(index % gridLayout.columns) === 2 ? "yaw_pos_gain" :
										"yaw_neg_gain")
						
                        // Track the text of each TextField
                        onTextChanged: {
                            textData[index] = text
                        }
                    }
                }
            }

				}

				Rectangle{
					
					width: control_type_page.width
					height: 50
					color: "blue"

					// Button to log data
            Button {
                text: "save"

                onClicked: {

					console.log("Logging all TextField data:");
                    for (var i = 0; i < textData.length; i++) {
                        // Only log text if it's not undefined or an empty string
                        if (textData[i] && textData[i].trim() !== "") {
                            console.log("Baris " + (Math.floor(i / gridLayout.columns) + 1) +
                                        ", Kolom " + ((i % gridLayout.columns) + 1) +
                                        ": " + textData[i]);
							let row = Math.floor(i / gridLayout.columns);
							let col = (i % gridLayout.columns);
							let val = textData[i];

							backend.fsm_gain(row.toString(), col.toString(), val);
														
						}
                    
					}

					

					
                }
            }
					
				}


			Rectangle{
					
					width: control_type_page.width
					height: 150
					color: "pink"

			}
				
			
			}

        }
    
	
	
	}	




		}


		Rectangle{
			id : navigation_page
			anchors.centerIn: parent
			height: 450
			width : 750
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"
			visible : false

			Rectangle{
			x : 0
			y : 0
			height: 450
			width : 750/2
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"

			Text{
			anchors.horizontalCenter: parent.horizontalCenter
			y : 5
			text : "GPS SETTING"
			font.pixelSize : 18
			color : "#00ff00"
			font.family: "Helvetica"
			}

			Text{
			x : 5
			y : 70
			text : "GPS Type       :"
			font.pixelSize : 15
			color : "#00ff00"
			font.family: "Helvetica"
			}

			ComboBox {
				x : 135
				y : 70
				model: ["GPS NEO 6M", "EMLID RTK", "EMLID GNSS"]
				height : 25
				width : 200
			}

			Text{
			x : 5
			y : 110
			text : "Communication :"
			font.pixelSize : 15
			color : "#00ff00"
			font.family: "Helvetica"
			}

			ComboBox {
				x : 135
				y : 110
				model: ["SERIAL", "MQTT"]
				height : 25
				width : 200
			}

			Text{
			x : 5
			y : 150
			text : "GPS Filtering :"
			font.pixelSize : 15
			color : "#00ff00"
			font.family: "Helvetica"
			}

			ComboBox {
				x : 135
				y : 150
				model: ["None", "Moving Average Filter", "Kalman Filter"]
				height : 25
				width : 200
			}


			Rectangle{
			x : 0
			y : 200
			height: 450/2 + 22
			width : 750/4
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"

				Text{
					anchors.horizontalCenter: parent.horizontalCenter
					y : 5
					text : "GPS Filter"
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				
				Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 5
					y :25
					text : "Moving Average Filter"
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 5
					y :45
					text : "W : "
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				Slider{
					id : weight_filter
					x : 10
					y : 65
					from : 0
					to : 1
					width : 150

					Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 140
					y :0
					text : (weight_filter.value).toFixed(2)
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}
				}


				Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 5
					y :100
					text : "Kalman Filter"
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 5
					y :120
					text : "Q : "
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				TextInput{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 35
					y :120
					text : "0.5"
					font.pixelSize : 15
					color : "#ffff33"
					font.family: "Helvetica"
					}

				Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 100
					y :120
					text : "R : "
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				TextInput{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 130
					y :120
					text : "1.0"
					font.pixelSize : 15
					color : "#ffff33"
					font.family: "Helvetica"
					}

			}

			Rectangle{
			x : 750/4
			y : 200
			height: 450/2 + 22
			width : 750/4
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"
				Text{
					anchors.horizontalCenter: parent.horizontalCenter
					y : 5
					text : "GPS Communication"
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 5
					y :25
					text : "MQTT Broker : 127.0.0.1"
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 5
					y :50
					text : "Serial Port"
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

				ComboBox {
				anchors.horizontalCenter: parent.horizontalCenter
				y : 80
				model: []
				height : 25
				width : 120
			}

			Text{
					//anchors.horizontalCenter: parent.horizontalCenter
					x : 5
					y :120
					text : "Baud rate"
					font.pixelSize : 15
					color : "#00ff00"
					font.family: "Helvetica"
					}

			ComboBox {
				anchors.horizontalCenter: parent.horizontalCenter
				y : 150
				model: [9600, 38400, 115200]
				height : 25
				width : 120

			}

			}

			}


			Rectangle{
			x : 750/2
			y : 0
			height: 450
			width : 750/2
			color :"transparent"
			border.width : 2
			border.color :"#00ff00"


			
			

			Item {
			id: page
		
			anchors.fill: parent
			width:parent.width
			height: parent.height
			
			
			ScrollView {
				id:scrollView
				anchors.fill:parent

            
				style: ScrollViewStyle {
					handle: Rectangle {
					x: 0
					implicitWidth: 10
					implicitHeight: 30
					color: "#7df9ff"
					
				}
				
				minimumHandleLength : 10
				
				scrollBarBackground: Rectangle {
					implicitWidth: 10
					implicitHeight: 30
					color: "transparent"
				}
				decrementControl: Rectangle {
					implicitWidth: 0
					implicitHeight: 0
					color: "transparent"
				}
				incrementControl: Rectangle {
					implicitWidth: 0
					implicitHeight: 0
					color: "transparent"
				}
			}
					
					Column{
						width:parent.width
						spacing:1
						
						Rectangle{
							id: rect1
							width: page.width 
							height: 500 + coloumn_rpl.height
							color: "transparent"

							Text{
							anchors.horizontalCenter: parent.horizontalCenter
							y : 5
							text : "Route Positioning List"
							font.pixelSize : 18
							color : "#00ff00"
							font.family: "Helvetica"
							}

					Rectangle{
						y : 50
						height: 250
						width: page.width
						color :"transparent"
						border.width : 2
						border.color :"#00ff00"

						Text{
							anchors.horizontalCenter: parent.horizontalCenter
							y : 5
							text : "Add Route List"
							font.pixelSize : 15
							color : "#00ff00"
							font.family: "Helvetica"
							}
						
						Text{
							x : 5
							y : 35
							text : "length (m) : "
							font.pixelSize : 15
							color : "#00ff00"
							font.family: "Helvetica"
							}
							
						TextField{
							id : length_manual
							x : 80
							y : 30
							text : ""
							font.pixelSize : 10
							height : 30
							width : 50
							color : "black"
							font.family: "Helvetica"
							}
							
						Text{
							x : 140
							y : 35
							text : "angle  : "
							font.pixelSize : 15
							color : "#00ff00"
							font.family: "Helvetica"
							}
							
						TextField{
							id : angle_manual
							x : 190
							y : 30
							text : ""
							font.pixelSize : 10
							height : 30
							width : 50
							color : "black"
							font.family: "Helvetica"
							}
							
						Button{
							
							x : 250
							y : 30
							width : 60
							text : "convert"

							Rectangle{
								width : parent.width
								height : parent.height
								color : "gray"
							}

							onClicked :{
								//latitude_position_value.text, longitude_position_value.text
								var result = rot_matrice(0, parseFloat(length_manual.text)/111000, parseFloat(angle_manual.text)-90);
								console.log("lat result:", result.y_accent);
								console.log("long result:", result.x_accent);
								lat_manual.text = parseFloat(latitude_position_value.text) + parseFloat(result.y_accent)
								long_manual.text = parseFloat(longitude_position_value.text) + parseFloat(result.x_accent)
								
								
							}
						}
						
						Text{
							x : 5
							y : 85
							text : "Latitude   : "
							font.pixelSize : 15
							color : "#00ff00"
							font.family: "Helvetica"
							}
						
						TextField{
							id : lat_manual
							x : 80
							y : 80
							text : ""
							font.pixelSize : 10
							height : 30
							width : 150
							color : "black"
							font.family: "Helvetica"
							}

						Text{
							x : 5
							y : 125
							text : "Longitude : "
							font.pixelSize : 15
							color : "#00ff00"
							font.family: "Helvetica"
							}
						
						TextField{
							id : long_manual
							x : 80
							y : 120
							text : ""
							font.pixelSize : 10
							height : 30
							width : 150
							color : "black"
							font.family: "Helvetica"
							}

						Button{
							id : add_route
							x : 250
							y : 80
							height : 73
							width : 73
							text : "add"

							Rectangle{
								width : parent.width
								height : parent.height
								color : "gray"
							}

							onClicked :{

								var coordinate = QtPositioning.coordinate(lat_manual.text, long_manual.text);
								markerModel.append({"latitude": lat_manual.text, "longitude": long_manual.text});
								var text = md.count + 1;
								md.append({"coords": coordinate, "title": text});
								li.addCoordinate(coordinate)
								backend.rpl_point(lat_manual.text, long_manual.text)


							}
						}

						Button{
							
							//anchors.horizontalCenter: parent.horizontalCenter
							x : 5
							y : 160
							height : 40
							width : 200
							text : "Browse CSV file"
							onClicked:{
								fileDialog.visible = true
							}
						}

						Button{
							
							//anchors.horizontalCenter: parent.horizontalCenter
							x : 220
							y : 160
							height : 40
							width : 100
							text : "Update Map"
							onClicked:{
								upload_csv()
							}
						}

						FileDialog {
							id: fileDialog
							title: "Please choose a file"
							folder: shortcuts.home
							//selectFolder : true
							visible : false
						
						onAccepted: {
							console.log("You chose: " + fileDialog.fileUrls)
							backend.folder_read(fileDialog.fileUrls)
							fileDialog.visible = false
						}
						
						onRejected: {
							console.log("Canceled")
							fileDialog.visible = false
						}
						
						}
						

					}

					Rectangle{
						//anchors.horizontalCenter: parent.horizontalCenter
						y :310
						height: 80 + coloumn_rpl.height
						width: page.width
						color :"transparent"
						border.width : 2
						border.color :"#00ff00"

						Text{
							anchors.horizontalCenter: parent.horizontalCenter
							y : 5
							text : "Route Positioning List"
							font.pixelSize : 15
							color : "#00ff00"
							font.family: "Helvetica"
							}

					Rectangle {
						//anchors.horizontalCenter: parent.horizontalCenter
						x : 30
						y : 40
						color : "transparent"	
						Column {
							id : coloumn_rpl
							//y : 30
							//anchors.fill: parent

						Repeater {
							model: rpl_lat.length
							x : 5
							Row {
								Text {
										text: index + 1 // Nomor indeks dimulai dari 1
										width: 30
										font.pixelSize : 15
										color : "#00ff00"
										font.family: "Helvetica"
									}

								Text {
										text: rpl_lat[index] // Mengakses elemen dengan indeks yang sama dari x
										font.pixelSize : 15
										color : "#00ff00"
										font.family: "Helvetica"
									}
								Text {
										text : "    "
									}
								Text {
										text: (typeof rpl_long[index] !== 'undefined') ? rpl_long[index] : "" // Periksa jika nilai tidak terdefinisi
										font.pixelSize : 15
										color : "#00ff00"
										font.family: "Helvetica"
									}
								}
						}
						
							
					}

					}


					}

				}

			}

        }
	}
			}
		}
    }

	Component.onCompleted: {
                
				points = backend.points()
				console.log(points)
				points2 = backend.points2()
				drawAll();
            }

	property var rpl_lat: []
	property var rpl_long: []

	property var rpl_index:[]
	property var rpl_index_prev:[]

	
	onClosing: {
        capture.stop()
		reconnect_button.checked = false
		//capture_signal.visible = false
		}
	
	
	function drawAll() {
            // Bersihkan map
			/* Hapus semua item KECUALI marker kapal
			for (var i = map.mapItems.length - 1; i >= 0; i--) {
				if (map.mapItems[i] !== marker) {  // ⛔ Jangan hapus kapal
					map.removeMapItem(map.mapItems[i]);
				}
			}
			*/
            

            // Tambahkan MapCircle dan Label
            for (var i = 0; i < points.length; i++) {
                var p = points[i];

                var circle = Qt.createQmlObject(`
                    import QtLocation 5.11
                    import QtPositioning 5.11
                    MapCircle {
                        center: QtPositioning.coordinate(${p.latitude}, ${p.longitude})
                        radius: 10
                        color: "#46a2da"
                        border.color: "${p.color}"
                        border.width: 3
                    }
                `, map, "Circle_" + i);
                map.addMapItem(circle);

                var label = Qt.createQmlObject(`
                    import QtQuick 2.12
                    import QtLocation 5.11
                    import QtPositioning 5.11
                    MapQuickItem {
                        coordinate: QtPositioning.coordinate(${p.latitude}, ${p.longitude})
                        anchorPoint.x: 40
                        anchorPoint.y: 60
                        sourceItem: Rectangle {
                            color: "white"
                            border.color: "black"
                            border.width: 1
                            radius: 4
                            width: textItem.paintedWidth + 10
                            height: textItem.paintedHeight + 6

                            Text {
                                id: textItem
                                text: "${p.name}"
                                anchors.centerIn: parent
                                color: "black"
                                font.pointSize: 10
                                font.bold: true
                            }
                        }
                    }
                `, map, "Label_" + i);
                map.addMapItem(label);
            }

            // Tambahkan garis antar titik (segment warna sesuai titik awal)
            for (var j = 0; j < points.length - 1; j++) {
                var p1 = points[j];
                var p2 = points[j + 1];

                var line = Qt.createQmlObject(`
                    import QtLocation 5.11
                    import QtPositioning 5.11
                    MapPolyline {
                        line.width: 4
                        line.color: "${p1.color}"
                        path: [
                            QtPositioning.coordinate(${p1.latitude}, ${p1.longitude}),
                            QtPositioning.coordinate(${p2.latitude}, ${p2.longitude})
                        ]
                    }
                `, map, "Line_" + j);
                map.addMapItem(line);
            }
        
		
		
			// Tambahkan Jalur 2
			for (var i = 0; i < points2.length; i++) {
				var p = points2[i];

				var circle = Qt.createQmlObject(`
					import QtLocation 5.11
					import QtPositioning 5.11
					MapCircle {
						center: QtPositioning.coordinate(${p.latitude}, ${p.longitude})
						radius: 10
						color: "#46a2da"
						border.color: "${p.color}"
						border.width: 3
					}
				`, map, "Circle2_" + i);
				map.addMapItem(circle);

				var label = Qt.createQmlObject(`
					import QtQuick 2.12
					import QtLocation 5.11
					import QtPositioning 5.11
					MapQuickItem {
						coordinate: QtPositioning.coordinate(${p.latitude}, ${p.longitude})
						anchorPoint.x: 40
						anchorPoint.y: 60
						sourceItem: Rectangle {
							color: "white"
							border.color: "black"
							border.width: 1
							radius: 4
							width: textItem.paintedWidth + 10
							height: textItem.paintedHeight + 6

							Text {
								id: textItem
								text: "${p.name}"
								anchors.centerIn: parent
								color: "black"
								font.pointSize: 10
								font.bold: true
							}
						}
					}
				`, map, "Label2_" + i);
				map.addMapItem(label);
			}

			// Garis antar titik Jalur 2
			for (var j = 0; j < points2.length - 1; j++) {
				var p1 = points2[j];
				var p2 = points2[j + 1];

				var line = Qt.createQmlObject(`
					import QtLocation 5.11
					import QtPositioning 5.11
					MapPolyline {
						line.width: 4
						line.color: "${p1.color}"
						path: [
							QtPositioning.coordinate(${p1.latitude}, ${p1.longitude}),
							QtPositioning.coordinate(${p2.latitude}, ${p2.longitude})
						]
					}
				`, map, "Line2_" + j);
				map.addMapItem(line);
			}

					
					
					}



	Timer{
		id:depthtimer
		interval: 2000
		repeat: true
		running: true
		onTriggered: {
			
			//backend.estimate_depth(latitude_rov_value.text, longitude_rov_value.text)
			backend.estimate_depth((latitude_position_value.text), (longitude_position_value.text))

			depth_est.text = "depth est : " + backend.est() + " m"

			if (line1.checked == true){
				upload_csv()
				backend.estimate_rpl(1)
			
			}
			
			if (line2.checked == true){
				upload_csv()
				backend.estimate_rpl(2)
			}

		}
		
	}



	Timer{
		id:controller_gui
		interval: 100
		repeat: true
		running: true
		onTriggered: {

		drive_mode.text = "drive mode : "+ backend.drive_mode()
		

		navigation_mode_var = backend.drive_mode()
		if (navigation_mode_var != navigation_mode_var_prev){
			
			if (navigation_mode_var == "station keeping"){
				
				//backend.rpl_point(latitude_position_value.text, longitude_position_value.text)
				print("station keeping")
			}

			if (navigation_mode_var_prev == "station keeping"){
				backend.remove("back")
			}

			if (navigation_mode_var == "line route"){
				autopilot_button.checked = true
			} else {
				autopilot_button.checked = false
			}
			


			
			

		}
		
		
		rpl_lat = backend.rpl_lat()
		rpl_long = backend.rpl_long()
		rpl_index = rpl_lat.length

		if (rpl_index != rpl_index_prev){
			console.log("update map")
			upload_csv()
		}

		//console.log(rpl_lat.length)
		//console.log(propeller1_position.x, propeller1_position.y)
		propeller1_properties.text = propeller1_position.x //+"\n"+ propeller1_position.y
		propeller2_properties.text = propeller2_position.x +"\n"+ propeller2_position.y
		propeller3_properties.text = propeller3_position.x +"\n"+ propeller3_position.y
		propeller4_properties.text = propeller4_position.x +"\n"+ propeller4_position.y
		cog_properties.text = cog.x +"\n"+ cog.y
		
		backend.tick("yes")
		control_prop.text = backend.control_prop()//"ṅ \nė \nψ_dot\nẋ\nẏ"
			
		gps_status.color = backend.gps_status_color()
		
        windSpeed_value.text = backend.windspeed()
        wind_direct_value.text = backend.winddirect()
        latitude_position_value.text = backend.lat()
        longitude_position_value.text = backend.long()
        heading_value.text = backend.headingship()
        markerdirect.angle = backend.headingship()
        
		//vessel1.rotation = backend.headingship()

        lat_target.text = backend.lat_target()
        long_target.text = backend.long_target()

        speed1.text = "Throttle : " + backend.Set_Speed1()
        speed2.text = "Throttle : " +backend.Set_Speed2()
        speed3.text = "Throttle : " +backend.Set_Speed3()
        speed4.text = "Throttle : " +backend.Set_Speed4()

        
        arrowkiridepan.rotation = backend.steering4()
        arrowkanandepan.rotation = backend.steering1()
		
		
        arrowkananbelakang.rotation = backend.steering2()
        arrowkiribelakang.rotation = backend.steering3()
		
		arrowkiridepan_target.rotation = backend.steering4_target()
        arrowkanandepan_target.rotation = backend.steering1_target()
		
		//console.log(backend.steering1_target())
		
        arrowkananbelakang_target.rotation = backend.steering2_target()
        arrowkiribelakang_target.rotation = backend.steering3_target()
		//console.log(backend.central_status())
		
		if (backend.central_status() == "local"){
			arrowkananbelakang_target.visible = false;
			arrowkiribelakang_target.visible = false;
			arrowkanandepan_target.visible = false;
			arrowkiridepan_target.visible = false;
		}
		
		if (backend.central_status() == "central"){
			arrowkananbelakang_target.visible = true;
			arrowkiribelakang_target.visible = true;
			arrowkanandepan_target.visible = true;
			arrowkiridepan_target.visible = true;
		}
		
		line_length.text = "line length : " + ruler_measurement.toFixed(1) + " m"	
		
		backend.autopilot(autopilot_button.checked)
		
		position_error.text = "position error : "+ backend.position_error() + " m"		
		dir_error.text = "dir error : " + backend.dir_error() + " °" + " Z: " + backend.zone()		
		heading_error.text = "heading error : " + backend.heading_error() + " °"
		
		
		if (heading_lock.checked){
			slider.visible = true
			slider.interactive = true
			console.log(slider.value)
			backend.heading_target_slot(slider.value)
		} else {
			slider.visible = false
			slider.interactive = false
			slider.value = backend.headingship()
		}
		//slider.value = backend.heading_target()
		
		
		//console.log(backend.heading_target())
		compass_val.text =  "<font color='gold'>" + slider.value + "</font>"
		

		//gov1.color


		gov1.color = backend.spc_indicator_color1()
		gov2.color = backend.spc_indicator_color2()
		gov3.color = backend.spc_indicator_color3()
		gov4.color = backend.spc_indicator_color4()

		speed1.color = backend.throttle_indicator_color1()
		speed2.color = backend.throttle_indicator_color2()
		speed3.color = backend.throttle_indicator_color3()
		speed4.color = backend.throttle_indicator_color4()

		ship_speed.text = backend.speed_ship()
		
		
		lat_long_dms_text.text = backend.latitude_dms()+backend.lat_pole()+"\n"+ backend.longitude_dms()+backend.long_pole()
			
		rpm1.text = "<font color='white'>" + backend.rpm1() + "</font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'>" +backend.target_rpm1()+ "</font>\nRPM"
		rpm2.text = "<font color='white'>" + backend.rpm2() + "</font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'>" +backend.target_rpm2()+ "</font>\nRPM"
		rpm3.text = "<font color='white'>" + backend.rpm3() + "</font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'>" +backend.target_rpm3()+ "</font>\nRPM"
		rpm4.text = "<font color='white'>" + backend.rpm1() + "</font>"+ "<font color='#D95204'> / </font>" + "<font color='gold'>" +backend.target_rpm4()+ "</font>\nRPM"


		latitude_destination.text = backend.latitude_target()
		longitude_destination.text = backend.longitude_target()

		
		pitch_filtered_sensor.text = backend.pitch()
		roll.text = backend.roll()

		rpl_index_prev = rpl_index
		

		steering1_status.border.color = "red"
		steering2_status.border.color = "red"
		steering3_status.border.color = "red"
		steering4_status.border.color = "red"
			
		navigation_mode.text = "steering mode : "+  backend.navigation_mode()
		
		control_style.text = "propeller command : " + backend.control_style()
		power.value = Math.abs(backend.power())

		power_color = backend.power() < 0 ? "#ff0000" : "#00ff00"
		
		navigation_mode_var_prev = navigation_mode_var
		heading_speed.text = "heading speed : " + backend.heading_speed() + "\nradius_zone : " + backend.radius_zone()
	
	
		radar_gauge.height = constrain(mapValue(backend.position_error(),0,100,0,75), 0, 75) //0, 100 meter
		radar.rotation = (backend.dir_error() - 180) 

		if (backend.joystick1_status() == "on" && backend.joystick2_status() == "on"){
			joystick_color.color = "#2BC088"
			joystick2_color.color = "#2BC088"
			joystick_selector.visible = true
			
			if(joystick_selector.on == true){
				backend.joystick_mode("2")
			} else {
				backend.joystick_mode("1")
			}
			
		
		} else {

			joystick_selector.visible = false

			if (backend.joystick1_status() == "on"){
				joystick_color.color = "#2BC088"
				backend.joystick_mode("1")
			} else {
				joystick_color.color = "#F7286E"
			}


			if (backend.joystick2_status() == "on"){
				joystick2_color.color = "#2BC088"
				backend.joystick_mode("2")
				
			} else {
				
				joystick2_color.color = "#F7286E"
			}


			if (backend.joystick1_status() == "off" && backend.joystick2_status() == "off"){
				backend.joystick_mode("0")
			}

			wind_attack.rotation = backend.winddirect()

		}
	}
		
}



	
}
