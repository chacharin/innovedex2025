# 📦 นำเข้าไลบรารี
import cv2                # สำหรับการอ่านภาพจากกล้องและแสดงผล
import zmq                # สำหรับสร้าง socket และส่งข้อมูลด้วย ZeroMQ
import json               # สำหรับแปลง dict เป็น string (JSON)
from ultralytics import YOLO  # โหลดโมเดล YOLOv8 ที่เทรนไว้แล้ว

# 🧠 โหลดโมเดลที่เราเทรนเอง (best.pt) ซึ่งได้จากการ train custom dataset
model = YOLO("best.pt")

# 🎥 เปิดกล้อง (0 หมายถึงกล้องตัวแรกที่เชื่อมต่อกับเครื่อง)
cap = cv2.VideoCapture(0)

# 🛠️ ตั้งค่าความละเอียดของกล้อง (สามารถปรับตามความต้องการ)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ✅ กำหนดค่าความเชื่อมั่นขั้นต่ำ (confidence threshold)
# เพื่อกรองการตรวจจับที่ไม่แม่นยำออก
CONFIDENCE_THRESHOLD = 0.5

# 🌐 สร้าง context และ socket สำหรับส่งข้อมูลแบบ Publisher
context = zmq.Context()
socket = context.socket(zmq.PUB)           # ใช้ socket แบบ PUB (Publisher)
socket.bind("tcp://localhost:5555")        # เปิดพอร์ต 5555 เพื่อให้ Subscriber เชื่อมต่อเข้ามา

# 🔁 วนลูปทำงานตลอดเวลา
while True:
    # 📸 อ่านภาพจากกล้อง
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")      # ถ้าอ่านไม่สำเร็จ ให้หยุดโปรแกรม
        break

    # 🔍 ใช้โมเดลตรวจจับวัตถุในภาพ
    results = model(frame)[0]              # ใช้ YOLO ตรวจจับ และเลือกผลลัพธ์ชุดแรก (batch index 0)
    boxes = results.boxes                  # ดึงกล่องที่ตรวจพบ (bounding boxes)

    detections = []  # 🔧 สร้าง list ว่างเพื่อเก็บข้อมูลที่ต้องการส่งออกไปผ่าน ZMQ

    # 🔁 วนลูปตรวจสอบวัตถุแต่ละชิ้นที่ถูกตรวจจับได้
    for box in boxes:
        conf = float(box.conf)             # ความมั่นใจ (confidence) ของกล่องนี้
        cls_id = int(box.cls[0])           # ID ของคลาสที่ถูกตรวจพบ (เช่น 0 = 'person')
        
        if conf >= CONFIDENCE_THRESHOLD:   # ✅ กรองเฉพาะกล่องที่มีความเชื่อมมั่นมากพอ
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # พิกัดมุมซ้ายบนและขวาล่างของกล่อง
            label = model.names[cls_id]    # ชื่อคลาสที่ตรวจจับได้ (จากไฟล์ .yaml)
            w, h = x2 - x1, y2 - y1        # คำนวณความกว้างและความสูงของกล่อง
            cx, cy = x1 + w // 2, y1 + h // 2  # หาศูนย์กลางของกล่อง (center x/y)

            # ➕ บันทึกข้อมูลของกล่องนี้ลงใน list เพื่อส่งผ่าน ZeroMQ
            detections.append({
                "label": label,
                "conf": round(conf, 2),
                "x": cx,        # center x
                "y": cy,        # center y
                "w": w,         # width
                "h": h          # height
            })

            # 🖍️ วาดกรอบแสดงผลบนภาพพร้อมชื่อคลาสและความเชื่อมั่น
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # วาดกรอบเขียว
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 📤 ถ้ามีข้อมูลการตรวจจับ → ส่งผ่าน ZeroMQ เป็น JSON string
    if detections:
        socket.send_string(json.dumps(detections))  # แปลง list → JSON string แล้วส่ง

    # 🖼️ แสดงภาพที่มีการวาดกรอบตรวจจับแล้วแบบ real-time
    cv2.imshow("YOLOv8 Detection", frame)

    # ⏹️ ถ้าผู้ใช้กด 'q' จะออกจากลูป
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 🧹 ปิดกล้องและหน้าต่างแสดงผลเมื่อสิ้นสุดโปรแกรม
cap.release()
cv2.destroyAllWindows()
