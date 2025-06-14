// File: SiriWave.qml
import QtQuick 2.15
import QtGraphicalEffects 1.15

Item {
    width: 600; height: 200
    property real waveAmplitude: 0.04
    property real waveFrequency: 6
    ShaderEffect {
        anchors.fill: parent
        property real time: 0
        fragmentShader: "
            varying vec2 qt_TexCoord0;
            uniform lowp float qt_Opacity;
            uniform highp float time, waveFrequency, waveAmplitude;
            void main() {
                lowp float x = qt_TexCoord0.x;
                highp float y = qt_TexCoord0.y;
                highp float sine = sin(time + waveFrequency * x * 6.28318);
                highp float offset = waveAmplitude * sine;
                gl_FragColor = vec4(0.0, 0.7 + offset, 1.0, qt_Opacity);
            }"
        NumberAnimation on time { from: 0; to: Math.PI*2; duration: 1200; loops: Animation.Infinite }
    }
}
