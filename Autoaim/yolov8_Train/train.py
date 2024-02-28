from ultralytics import YOLO
# Load a model
# model = YOLO('yolov8m-pose.yaml')  # build a new model from YAML
# model = YOLO('yolov8n-pose.pt')  # load a pretrained model (recommended for training)
model = YOLO('yolov8n-pose.yaml')  # build a new model from YAML
model = YOLO('yolov8n-pose.pt')  # load a pretrained model (recommended for training)

if __name__ == '__main__':
    # Train the model, device = 0 for GPU, device = 'cpu' for CPU
    model.train(data='armor-four-points.yaml', epochs=200, imgsz=416, device=0,batch=4)