import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QFileDialog, 
                            QAction, QWidget, QHBoxLayout, QMessageBox, 
                            QScrollArea, QSizePolicy)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QSize

class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置更大的默认字体
        font = QFont()
        font.setPointSize(12)  # 增大字体大小
        QApplication.setFont(font)
        
        self.initUI()
        self.original_image = None
        self.processed_image = None
        self.original_pixmap = None
        self.processed_pixmap = None
        
    def initUI(self):
        self.setWindowTitle('图像处理工具')
        
        # 设置更大的初始窗口尺寸 (宽度, 高度)
        self.setGeometry(100, 100, 1400, 800)  # 原为1200x700
        
        # 设置菜单栏字体
        menu_font = QFont()
        menu_font.setPointSize(10)
        self.menuBar().setFont(menu_font)
        
        self.createMenus()
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 使用水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # 增加一些边距
        layout.setSpacing(10)
        
        # 左侧 - 原始图像区域
        self.original_scroll = QScrollArea()
        self.original_scroll.setWidgetResizable(True)
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        # 设置标签字体
        label_font = QFont()
        label_font.setPointSize(10)
        self.original_label.setFont(label_font)
        
        self.original_scroll.setWidget(self.original_label)
        layout.addWidget(self.original_scroll, 1)
        
        # 右侧 - 处理后图像区域
        self.processed_scroll = QScrollArea()
        self.processed_scroll.setWidgetResizable(True)
        self.processed_label = QLabel()
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.processed_label.setFont(label_font)
        self.processed_scroll.setWidget(self.processed_label)
        layout.addWidget(self.processed_scroll, 1)
        
        main_widget.setLayout(layout)
        
        # 设置状态栏字体
        status_font = QFont()
        status_font.setPointSize(10)
        self.statusBar().setFont(status_font)
        self.statusBar().showMessage('准备就绪')
    
    def createMenus(self):
        # 文件菜单
        file_menu = self.menuBar().addMenu('文件')
        
        open_action = QAction('打开图像', self)
        open_action.setFont(QFont('Arial', 11))  # 设置菜单项字体
        open_action.triggered.connect(self.openImage)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存结果', self)
        save_action.setFont(QFont('Arial', 11))
        save_action.triggered.connect(self.saveImage)
        file_menu.addAction(save_action)
        
        exit_action = QAction('退出', self)
        exit_action.setFont(QFont('Arial', 11))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 直方图均衡化菜单项
        hist_action = QAction('直方图均衡化', self)
        hist_action.setFont(QFont('Arial', 11))
        hist_action.triggered.connect(self.histogramEqualization)
        self.menuBar().addAction(hist_action)
        
        # 边缘检测菜单项
        edge_action = QAction('边缘检测(Canny)', self)
        edge_action.setFont(QFont('Arial', 11))
        edge_action.triggered.connect(self.edgeDetection)
        self.menuBar().addAction(edge_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu('帮助')
        about_action = QAction('关于', self)
        about_action.setFont(QFont('Arial', 11))
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)
    
    def openImage(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "打开图像", "", 
                                                 "图像文件 (*.jpg *.jpeg *.png *.bmp);;所有文件 (*)", 
                                                 options=options)
        if file_path:
            try:
                # 使用numpy.fromfile读取（解决中文路径问题）
                with open(file_path, 'rb') as f:
                    img_array = np.frombuffer(f.read(), dtype=np.uint8)
                self.original_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if self.original_image is not None:
                    # 转换为QPixmap并保持原始像素数据
                    height, width, channel = self.original_image.shape
                    bytes_per_line = 3 * width
                    q_img = QImage(self.original_image.data, width, height, 
                                 bytes_per_line, QImage.Format_BGR888)
                    self.original_pixmap = QPixmap.fromImage(q_img)
                    
                    self.processed_image = None
                    self.processed_pixmap = None
                    self.displayImages()
                    self.statusBar().showMessage(f"已加载图像: {file_path}")
                else:
                    QMessageBox.warning(self, "错误", 
                                      f"无法加载图像文件\n路径: {file_path}\n"
                                      "可能原因:\n"
                                      "1. 文件路径包含特殊字符\n"
                                      "2. 文件已损坏\n"
                                      "3. 文件格式不受支持")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载图像时发生异常:\n{str(e)}")

    def saveImage(self):
        if self.processed_image is not None:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "保存图像", "", 
                                                     "JPEG (*.jpg *.jpeg);;PNG (*.png);;BMP (*.bmp);;所有文件 (*)", 
                                                     options=options)
            if file_path:
                try:
                    # 处理中文路径保存问题
                    ret, buf = cv2.imencode('.jpg', self.processed_image)
                    if ret:
                        with open(file_path, 'wb') as f:
                            buf.tofile(f)
                        self.statusBar().showMessage(f"图像已保存到: {file_path}")
                    else:
                        QMessageBox.warning(self, "错误", "无法编码图像")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"保存图像时发生异常:\n{str(e)}")
        else:
            QMessageBox.warning(self, "警告", "没有可保存的处理后图像")
    
    def histogramEqualization(self):
        if self.original_image is not None:
            # 转换为灰度图像
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            # 直方图均衡化
            equalized = cv2.equalizeHist(gray)
            # 将灰度图像转换为BGR格式以便显示
            self.processed_image = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
            
            # 转换为QPixmap
            height, width, channel = self.processed_image.shape
            bytes_per_line = 3 * width
            q_img = QImage(self.processed_image.data, width, height, 
                         bytes_per_line, QImage.Format_BGR888)
            self.processed_pixmap = QPixmap.fromImage(q_img)
            
            self.displayImages()
            self.statusBar().showMessage("已应用直方图均衡化")
        else:
            QMessageBox.warning(self, "警告", "请先加载图像")
    
    def edgeDetection(self):
        if self.original_image is not None:
            # 转换为灰度图像
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            # 使用Canny边缘检测
            edges = cv2.Canny(gray, 100, 200)
            # 将边缘图像转换为BGR格式以便显示
            self.processed_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # 转换为QPixmap
            height, width, channel = self.processed_image.shape
            bytes_per_line = 3 * width
            q_img = QImage(self.processed_image.data, width, height, 
                         bytes_per_line, QImage.Format_BGR888)
            self.processed_pixmap = QPixmap.fromImage(q_img)
            
            self.displayImages()
            self.statusBar().showMessage("已应用边缘检测(Canny)")
        else:
            QMessageBox.warning(self, "警告", "请先加载图像")
    
    def displayImages(self):
        """显示原始和处理后的图像"""
        # 显示原始图像
        if self.original_pixmap is not None:
            scaled_pixmap = self.original_pixmap.scaled(
                self.original_scroll.viewport().size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.original_label.setPixmap(scaled_pixmap)
            self.original_label.resize(scaled_pixmap.size())
        else:
            self.original_label.clear()
            self.original_label.setText("原始图像")
        
        # 显示处理后的图像
        if self.processed_pixmap is not None:
            scaled_pixmap = self.processed_pixmap.scaled(
                self.processed_scroll.viewport().size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.processed_label.setPixmap(scaled_pixmap)
            self.processed_label.resize(scaled_pixmap.size())
        else:
            self.processed_label.clear()
            self.processed_label.setText("处理后图像")
    
    def resizeEvent(self, event):
        """窗口大小改变时重新显示图像"""
        super().resizeEvent(event)
        self.displayImages()
    
    def showAbout(self):
        about_box = QMessageBox(self)
        about_box.setWindowTitle("关于")
    
        about_font = QFont()
        about_font.setPointSize(10)
        about_box.setFont(about_font)
    
        github_link = '<a href="https://github.com/rkwgit/image_processing.git">GitHub本项目代码</a>'
    
        about_box.setTextFormat(Qt.TextFormat.RichText)  # 启用富文本格式
        about_box.setText(
            "<b>图像处理工具 - 大窗口版</b><br><br>"
            "版本: 2.2<br><br>"
            "<b>功能特点:</b><br>"
            "- 更大的窗口和字体<br>"
            "- 支持中文路径<br>"
            "- 直方图均衡化<br>"
            "- 边缘检测(Canny)<br>"
            "- 前后对比显示<br><br>"  # 使用 <br> 代替 \n
            f"项目地址: {github_link}"
        )
        
        about_box.setTextFormat(Qt.RichText)
        about_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        
        about_box.exec_()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序默认字体
    font = QFont()
    font.setPointSize(12)
    app.setFont(font)
    
    # 设置Fusion样式，看起来更现代
    app.setStyle('Fusion')
    
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()