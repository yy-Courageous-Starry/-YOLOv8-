# 1. 导入YOLO类
from ultralytics import YOLO

if __name__ == "__main__":
    # 2. 加载模型---自己训练的best.pt
    model = YOLO(r"D:\workspace\人工智能-yolo目标检测\yolo26\runs\detect\train4\weights\best.pt")

    # ========== 只跑推理，注释掉val验证（如果不需要重复验证） ==========
    # model.val(
    #     data=r"D:\workspace\人工智能-yolo目标检测\yolo26\datasets\car\car.yaml",
    #     device=0,
    # )

    # 3. 执行推理
    results = model.predict(
        source=r"D:\workspace\人工智能-yolo目标检测\yolo26\datasets\hole\test\images",  # 统一D盘路径
        save=True,
        show=True,
        device=0,  # 用GPU推理，和验证时保持一致
    )
