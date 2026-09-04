#1.导入YOLO类
from ultralytics import YOLO


if __name__ == '__main__' :
    #2.加载模型---自己训练的best.pt
    model = YOLO(r"D:\workspace\人工智能-yolo目标检测\yolo26\runs\detect\train\weights\best.pt")
    #3.
    model.val(
        data=r"D:\workspace\人工智能-yolo目标检测\yolo26\datasets\car\car.yaml",
        device=0,
    )