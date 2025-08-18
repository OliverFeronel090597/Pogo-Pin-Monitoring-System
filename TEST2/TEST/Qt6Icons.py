import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QStyle


class IconViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QStyle Standard Icons Viewer")
        self.setMinimumSize(800, 600)

        scroll = QScrollArea()
        container = QWidget()
        layout = QVBoxLayout()

        # Group of icons to show
        icon_names = [
            "SP_ArrowBack",
            "SP_ArrowDown",
            "SP_ArrowForward",
            "SP_ArrowLeft",
            "SP_ArrowRight",
            "SP_ArrowUp",
            "SP_BrowserReload",
            "SP_BrowserStop",
            "SP_CommandLink",
            "SP_ComputerIcon",
            "SP_DesktopIcon",
            "SP_DialogApplyButton",
            "SP_DialogCancelButton",
            "SP_DialogCloseButton",
            "SP_DialogDiscardButton",
            "SP_DialogHelpButton",
            "SP_DialogNoButton",
            "SP_DialogOkButton",
            "SP_DialogOpenButton",
            "SP_DialogResetButton",
            "SP_DialogSaveButton",
            "SP_DialogYesButton",
            "SP_DirClosedIcon",
            "SP_DirHomeIcon",
            "SP_DirIcon",
            "SP_DirLinkIcon",
            "SP_DirOpenIcon",
            "SP_DockWidgetCloseButton",
            "SP_DriveCDIcon",
            "SP_DriveDVDIcon",
            "SP_DriveFDIcon",
            "SP_DriveHDIcon",
            "SP_DriveNetIcon",
            "SP_FileDialogBack",
            "SP_FileDialogContentsView",
            "SP_FileDialogDetailedView",
            "SP_FileDialogEnd",
            "SP_FileDialogInfoView",
            "SP_FileDialogListView",
            "SP_FileDialogNewFolder",
            "SP_FileDialogStart",
            "SP_FileIcon",
            "SP_FileLinkIcon",
            "SP_MediaPause",
            "SP_MediaPlay",
            "SP_MediaSeekBackward",
            "SP_MediaSeekForward",
            "SP_MediaSkipBackward",
            "SP_MediaSkipForward",
            "SP_MediaStop",
            "SP_MessageBoxCritical",
            "SP_MessageBoxInformation",
            "SP_MessageBoxQuestion",
            "SP_MessageBoxWarning",
            "SP_RestoreDefaultsButton",
            "SP_TitleBarCloseButton",
            "SP_TitleBarContextHelpButton",
            "SP_TitleBarMaxButton",
            "SP_TitleBarMenuButton",
            "SP_TitleBarMinButton",
            "SP_TitleBarNormalButton",
            "SP_TitleBarShadeButton",
            "SP_TitleBarUnshadeButton",
            "SP_ToolBarHorizontalExtensionButton",
            "SP_ToolBarVerticalExtensionButton",
            "SP_TrashIcon",
            "SP_VistaShield",
            "SP_CustomBase"
        ]


        for icon_name in icon_names:
            try:
                icon_enum = getattr(QStyle.StandardPixmap, icon_name)
                icon = QApplication.style().standardIcon(icon_enum)
                pixmap = icon.pixmap(32, 32)

                row = QHBoxLayout()
                label_icon = QLabel()
                label_icon.setPixmap(pixmap)
                label_text = QLabel(icon_name)
                label_text.setStyleSheet("font-family: Consolas; font-size: 14px;")

                row.addWidget(label_icon)
                row.addWidget(label_text)
                row.addStretch()
                layout.addLayout(row)

            except AttributeError:
                print(f"Invalid icon name: {icon_name}")

        container.setLayout(layout)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = IconViewer()
    viewer.show()
    sys.exit(app.exec())
