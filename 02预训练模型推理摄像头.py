#1.导入YOLO类
from ultralytics import YOLO

if __name__ == '__main__':
#2.加载模块
    model = YOLO("yolo26n.pt")

#3.设置检测的资源
source = 0
#4.模型推理 --- predict方法
"""
    predict方法的参数，可以在官网手册中找到，重要的如下：
    1.source：检测的资源
    2.save：是否保存
    3.show：是否显示结果【配合摄像头使用】
    4.device：推理的设备，GPU写0
返回值只有一个，是列表
"""
results = model.predict(
    source=source,
    save= True,
    device = 0,
    show = True
)
