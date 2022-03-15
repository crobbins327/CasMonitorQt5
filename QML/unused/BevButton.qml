import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Controls.impl 2.12
import QtQuick.Templates 2.12 as T

Button {
    id: bevButton
    font.capitalization: Font.MixedCase
    contentItem: IconLabel {
           spacing: bevButton.spacing
           mirrored: bevButton.mirrored
           display: bevButton.display

           icon: bevButton.icon
           text: bevButton.text
           font: bevButton.font
           color: bevButton.checked || bevButton.highlighted ? bevButton.palette.brightText :
                  bevButton.flat && !bevButton.down ? (bevButton.visualFocus ? bevButton.palette.highlight : bevButton.palette.windowText) : bevButton.palette.buttonText
       }

    background: Rectangle {
            implicitWidth: 100
            implicitHeight: 40
            border.color: bevButton.palette.highlight
            border.width: bevButton.visualFocus ? 2 : 0
            radius: 4

            color: Color.blend(bevButton.checked || bevButton.highlighted ? bevButton.palette.dark : bevButton.palette.button,
                                                                                bevButton.palette.mid, bevButton.down ? 0.5 : 0.0)
        }
}



