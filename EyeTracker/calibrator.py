import numpy as np
class Calibrator:
    """
    校准器，用于校准屏幕与摄像头的相对位置
    实现需求中的第9步：根据用户看显示屏（上、下、左、右、中）5个校准点的视线方向，
    校准显示屏与摄像头的相对位置
    """
    def __init__(self):
        """
        初始化校准器
        """
        self.calibration_points = []
        self.is_calibrated = False
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        
    def add_calibration_point(self, screen_x, screen_y, gaze_x, gaze_y):
        """
        添加校准点
        
        Args:
            screen_x: 屏幕x坐标 (0-1)
            screen_y: 屏幕y坐标 (0-1)
            gaze_x: 视线x坐标
            gaze_y: 视线y坐标
        """
        self.calibration_points.append((screen_x-0.5, screen_y-0.5, gaze_x, gaze_y))
        
    def calibrate(self):
        """
        根据校准点计算变换参数
        """
        if len(self.calibration_points) < 3:
            raise ValueError("至少需要3个校准点")
            
        # 提取数据
        screen_points = np.array([[p[0], p[1]] for p in self.calibration_points])
        gaze_points = np.array([[p[2], p[3]] for p in self.calibration_points])
        
        # 使用线性回归计算变换参数
        # 简化版：线性映射
        gaze_min = np.min(gaze_points, axis=0)
        gaze_max = np.max(gaze_points, axis=0)
        screen_min = np.min(screen_points, axis=0)
        screen_max = np.max(screen_points, axis=0)
        
        # 计算缩放因子
        self.scale_x = (screen_max[0] - screen_min[0]) / (gaze_max[0] - gaze_min[0]) if gaze_max[0] != gaze_min[0] else 1
        self.scale_y = (screen_max[1] - screen_min[1]) / (gaze_max[1] - gaze_min[1]) if gaze_max[1] != gaze_min[1] else 1
        
        # 计算偏移量
        self.offset_x = screen_min[0] - self.scale_x * gaze_min[0]
        self.offset_y = screen_min[1] - self.scale_y * gaze_min[1]
        
        self.is_calibrated = True
        
    def map_to_screen(self, gaze_x, gaze_y):
        """
        将视线坐标映射到屏幕坐标
        
        Args:
            gaze_x: 视线x坐标
            gaze_y: 视线y坐标
            
        Returns:
            屏幕坐标 (x, y) 范围在0-1之间
        """
        if not self.is_calibrated:
            # 如果未校准，返回默认值
            return (0.5, 0.5)
            
        screen_x = self.scale_x * gaze_x + self.offset_x
        screen_y = self.scale_y * gaze_y + self.offset_y
        
        # 限制在0-1范围内
        screen_x = max(-0.5, min(0.5, screen_x))+0.5
        screen_y = max(-0.5, min(0.5, screen_y))+0.5
        
        return (screen_x, screen_y)