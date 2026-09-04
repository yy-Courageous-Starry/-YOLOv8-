# 1.导入YOLO类
from ultralytics import YOLO

if __name__ == "__main__":
    # 2.加载模型---迁移学习【基于yolo26.pt预训练模型】
    model = YOLO("yolo26n.pt")

    # 3.调用train方法训练模型
    """
    train方法的参数一样可以在官网参考手册找到，掌握的如下：
        1.data:训练数据集的访问路径的配置文件的访问路径，即car，yaml
        2.epochs：训练的轮次，默认值100【不能很小，否则模型无效果】
        3.batch：训练的轮次中每个批次处理多少张图片，默认16【这个值会受到显存的限制，如果现存不大设置小一点】
        4.device：训练的设备，GPU写0
        5.workers：工作的线程数，默认值8【如果显存等不够，运行报错，设置小一点】
    """
    model.train(
        data=r"D:\workspace\人工智能-yolo目标检测\yolo26\datasets\car\car.yaml",
        epochs=100,
        batch=12,
        device=0,
        workers=4,
    )
