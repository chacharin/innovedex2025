# 🔌 นำเข้าไลบรารี zmq (ZeroMQ) สำหรับการสื่อสารแบบ socket-based และ json สำหรับจัดการข้อมูล
import zmq
import json

# ✅ สร้าง context ซึ่งเป็น environment สำหรับจัดการ socket หลายตัวใน ZeroMQ
context = zmq.Context()

# ✅ สร้าง socket แบบ SUB (Subscriber) → ใช้สำหรับ "รับข้อมูล" จาก Publisher
socket = context.socket(zmq.SUB)

# 📡 เชื่อมต่อกับ Publisher ที่อยู่บน address ที่กำหนด
# หาก Publisher และ Subscriber อยู่บนเครื่องเดียวกัน ให้ใช้ "localhost"
# หากต่างเครื่องให้ใช้ "tcp://<IP>:5555" เช่น "tcp://192.168.1.100:5555"
socket.connect("tcp://localhost:5555")

# ✅ ตั้งค่าให้ Subscriber รับข้อความทั้งหมดจาก Publisher
# ถ้าอยากกรองเฉพาะหัวข้อ (topic) ต้องระบุ prefix เช่น b"person" → แต่ "" หมายถึงรับทุกข้อความ
socket.setsockopt_string(zmq.SUBSCRIBE, "")

# 🔁 วนลูปรอรับข้อความจาก Publisher อย่างต่อเนื่อง
while True:
    # 📩 รับข้อความจาก Publisher (ข้อความที่ส่งมาจะเป็น JSON string)
    message = socket.recv_string()

    # 🔄 แปลงข้อความ JSON (string) ที่รับมาให้กลายเป็น Python object (list of dict)
    # เช่น [{'label': 'person', 'x': 300, 'y': 200, 'w': 100, 'h': 150, 'conf': 0.89}]
    detections = json.loads(message)

    # 🔍 วนลูปแสดงผลการตรวจจับแต่ละรายการ
    for det in detections:
        # แสดงข้อมูล label, center x/y, ความกว้าง/สูง, และความเชื่อมั่น
        print(f"[{det['label']}] x={det['x']} y={det['y']} w={det['w']} h={det['h']} conf={det['conf']}")
