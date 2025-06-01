# 📦 นำเข้าไลบรารีหลักที่ใช้ในโปรแกรม
import cv2                          # สำหรับเปิดกล้องและแสดงภาพ (OpenCV)
from ultralytics import YOLO       # สำหรับโหลดและใช้งาน YOLOv8 ที่เทรนไว้แล้ว

# 🧠 โหลดโมเดล YOLOv8 ที่เราเทรนเองไว้ (best.pt)
# หมายเหตุ: โมเดลนี้ควรอยู่ในโฟลเดอร์เดียวกับไฟล์ script หรือระบุ path ให้ถูกต้อง
model = YOLO("best.pt")

# 🎥 เปิดการเชื่อมต่อกล้อง (0 หมายถึงกล้องตัวแรกของระบบ — เช่น webcam)
cap = cv2.VideoCapture(0)

# 🛠️ กำหนดขนาดความละเอียดของกล้อง (จะช่วยควบคุม frame rate และขนาดการประมวลผล)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ✅ ตั้งค่าความเชื่อมั่นขั้นต่ำที่ยอมรับ (ค่าระหว่าง 0.0 ถึง 1.0)
CONFIDENCE_THRESHOLD = 0.5

# 🔁 วนลูปอย่างต่อเนื่องเพื่ออ่านภาพจากกล้องและตรวจจับวัตถุ
while True:
    # 📸 อ่านภาพจากกล้อง
    ret, frame = cap.read()

    # 🧯 ถ้าอ่านภาพไม่ได้ (กล้อง error หรือหลุด) ให้ออกจากลูป
    if not ret:
        print("Failed to grab frame")
        break

    # 🔍 ส่งภาพให้โมเดล YOLO ตรวจจับ (model(frame) คืนค่าผลตรวจจับทั้งหมด)
    results = model(frame)[0]  # [0] หมายถึง batch แรก (เพราะ YOLO รองรับหลายภาพพร้อมกัน)

    # 📦 ดึงกล่องทั้งหมดที่ตรวจพบจากผลลัพธ์
    boxes = results.boxes

    # 🔁 วนลูปผ่านกล่องตรวจจับทั้งหมด เพื่อกรองและแสดงเฉพาะที่ต้องการ
    for box in boxes:
        conf = float(box.conf)           # ค่าความมั่นใจของกล่องนี้ (0.0 ถึง 1.0)
        cls_id = int(box.cls[0])         # ดึงหมายเลขคลาสที่ตรวจพบ (เช่น 0, 1, 2)

        # ✅ กรองเฉพาะกล่องที่ความเชื่อมั่นเกิน threshold ที่เรากำหนดไว้
        if conf >= CONFIDENCE_THRESHOLD:
            # 🔢 แปลงพิกัดของกรอบ (Bounding Box) เป็นค่าจำนวนเต็ม
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # มุมบนซ้าย → ล่างขวา

            # 🔖 หาชื่อคลาสจาก ID (ใช้ model.names ซึ่งโหลดจาก YAML model)
            label = model.names[cls_id]

            # 🎨 สีของกรอบ (เขียว)
            color = (0, 255, 0)

            # 🖍️ วาดกรอบลงบนภาพ
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # 🏷️ ใส่ label และค่าความเชื่อมั่นบนภาพ
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # 🖼️ แสดงผลลัพธ์ภาพที่ผ่านการตรวจจับแบบ real-time
    cv2.imshow("YOLOv8 Custom Detection", frame)

    # ⏹️ ออกจากลูปถ้าผู้ใช้กดปุ่ม 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 🧹 ปิดการเชื่อมต่อกล้องและหน้าต่างเมื่อสิ้นสุดโปรแกรม
cap.release()
cv2.destroyAllWindows()
