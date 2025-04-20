from flask import Flask, request, render_template, jsonify
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from collections import Counter
import os
import uuid

app = Flask(__name__)

model = YOLO("bestv11vip.pt")  # Thay bằng model của bạn
UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

insect_info = {
    "Aphidoidea": "Rệp vừng (Tên khoa học: Aphididae) là một họ côn trùng trong bộ cánh nữa Hemiptera. Đây là những loài gây hại cho con người, trong đó có hai loại rệp vừng là rệp vừng trên khoai tây, kích thước của chúng đạt 3m/m, màu hồng nhạt hoặc màu xanh lá cây và loại rệp vừng đào xanh  nhỏ con hơn loại trên dài khoãng 1,5m/m có màu xanh lá cây nhạt đến đậm. Rệp vừng rất nhỏ, có hình dáng giống như trái lê, sống thành từng nhóm và sinh sản không cần giao hợp, rệp vừng có thể đi từ cây nầy sang cây khác, nhộng không có cánh, con lớn thì có loại có cánh có loại không, loại có cánh có thể bay đi rất xa hằng cây số theo gió và đáp xuống nơi nào thì nơi đó sẻ bị tràn lan bởi rệp vừng, chúng bám đầy lá ở mặt dưới, chúng là một loại côn trùng hút nhựa cây nguy hiểm nếu không kiểm soát được sẽ nhanh chóng lan rộng. Chúng thường tụ tập xung quanh mô mềm của chồi, đặc biệt là các đỉnh chồi, phần đốt thân và phần dưới lá, chúng hút nhựa và tạo ra những vùng nhạt màu trên lá.",
    "Beet Armyworm": "Beet Armyworm, (Tên khoa học là Spodoptera exigua) là một loài sâu hại nguy hiểm thuộc họ bướm đêm (Noctuidae), phân bố rộng ở vùng nhiệt đới và cận nhiệt đới. Sâu có tập tính ăn tạp, gây hại trên hơn 90 loại cây trồng như ngô, cải, cà chua, bông, khoai tây… Giai đoạn ấu trùng (sâu non) là gây hại mạnh nhất, chủ yếu ăn lá và bộ phận non, làm giảm năng suất nghiêm trọng. Con trưởng thành là bướm đêm nhỏ, cánh xám nâu. Để phòng trừ, có thể dùng biện pháp sinh học (ong ký sinh, vi khuẩn Bt), hóa học (Emamectin, Spinosad…) kết hợp canh tác hợp lý và giám sát bằng bẫy đèn hoặc pheromone. Beet Armyworm cần được theo dõi chặt chẽ để tránh phát sinh thành dịch.",
    "Bemisia Tabaci": "Bemisia tabaci, hay bọ phấn trắng, là loài côn trùng chích hút gây hại trên nhiều loại cây trồng như cà chua, ớt, đậu, dưa leo... Chúng có kích thước nhỏ, cơ thể phủ lớp phấn trắng và thường sống ở mặt dưới lá. Bọ phấn trắng gây hại bằng cách hút nhựa cây, làm cây vàng lá, giảm năng suất và còn tiết mật ngọt gây nấm bồ hóng. Đặc biệt, chúng là môi giới truyền nhiều loại virus gây bệnh cho cây trồng. Biện pháp phòng trừ gồm sử dụng thiên địch (ong ký sinh, nấm xanh, nấm trắng), thuốc hóa học (Imidacloprid, Buprofezin...) và vệ sinh đồng ruộng kết hợp bẫy vàng dính. Đây là đối tượng nguy hiểm cần theo dõi chặt chẽ trong sản xuất nông nghiệp.",
    "Black Hairy Caterpillar": "Black Hairy Caterpillar (sâu lông đen) là ấu trùng của một số loài bướm đêm, thuộc họ Erebidae, có cơ thể phủ đầy lông màu đen, gây cảm giác ngứa, rát hoặc kích ứng da khi chạm vào. Chúng là loài sâu ăn tạp, thường xuất hiện và gây hại nghiêm trọng trên nhiều loại cây trồng như đậu, bông, mè, ngô, lúa và các loại rau màu khác. Giai đoạn sâu non là thời kỳ phá hoại mạnh nhất, chúng ăn trụi lá, để lại trơ cành, khiến cây không thể quang hợp, dễ suy kiệt và chết. Khi mật độ cao, sâu có thể gây rụng lá hàng loạt, ảnh hưởng nghiêm trọng đến năng suất, nhất là ở các vùng canh tác tập trung. Sâu thường bộc phát mạnh vào mùa mưa, nhất là sau những đợt mưa lớn, do điều kiện ẩm ướt thuận lợi cho trứng nở và sâu non phát triển.",
    "Field Cricket": "Field Cricket (dế đồng) là một loài côn trùng thuộc họ Gryllidae, thường sinh sống ở đồng ruộng, bờ cỏ, ven vườn hoặc các khu vực đất trống có thảm thực vật thấp. Dế có màu nâu đen, cơ thể dài khoảng 2–3 cm, với đôi chân sau phát triển mạnh giúp nhảy xa và di chuyển nhanh. Loài này hoạt động chủ yếu vào ban đêm và phát ra âm thanh đặc trưng bằng cách cọ xát hai cánh trước để gọi bạn tình, đặc biệt vào mùa sinh sản.Dù không phải là đối tượng gây hại nghiêm trọng như sâu bệnh khác, nhưng Field Cricket có thể gây thiệt hại cho cây trồng khi mật độ cao. Chúng thường cắn phá mầm, rễ và lá non, đặc biệt trong giai đoạn gieo hạt và cây con, làm giảm tỷ lệ nảy mầm và ảnh hưởng đến sinh trưởng. Ngoài ra, dế còn có tập tính đào hang trong đất, gây xáo trộn vùng rễ và làm giảm độ ổn định của cây.",
    "Grasshopper": "Grasshopper (châu chấu) là loài côn trùng thuộc bộ cánh thẳng (Orthoptera), thường gặp nhiều ở đồng ruộng, bãi cỏ và ven rừng. Chúng có thân dài, màu xanh hoặc nâu, với đôi chân sau rất khỏe dùng để bật nhảy xa và cánh để bay. Châu chấu hoạt động mạnh vào ban ngày, nhất là khi thời tiết khô ráo và nắng nóng. Loài này gây hại bằng cách ăn lá, thân non và bông hoa của nhiều loại cây trồng như lúa, bắp, rau màu… Ở mật độ cao, chúng có thể phá hoại nghiêm trọng, làm trơ trụi lá, ảnh hưởng đến quá trình quang hợp và phát triển của cây. Một số loài châu chấu di cư theo đàn với số lượng lớn có thể tàn phá cả cánh đồng trong thời gian ngắn.",
    "Leaf Beetle": "Leaf Beetle (bọ cánh cứng ăn lá) là loài côn trùng thuộc họ Chrysomelidae, thường có kích thước nhỏ (dưới 1 cm), màu sắc đa dạng như xanh kim loại, vàng hoặc nâu. Chúng xuất hiện phổ biến trên nhiều loại cây trồng như rau màu, lúa, bắp, đậu, và một số cây công nghiệp như bông và thuốc lá. Cả ấu trùng và con trưởng thành đều gây hại bằng cách ăn lá, tạo thành các lỗ thủng hoặc ăn trụi mép lá, khiến cây suy yếu, chậm phát triển và giảm năng suất. Khi mật độ cao, bọ có thể gây rụng lá hàng loạt, ảnh hưởng nghiêm trọng đến quang hợp và khả năng sinh trưởng của cây.",
    "Nilaparvata Lugens": "Nilaparvata lugens (rầy nâu) là một trong những loài côn trùng hại lúa nguy hiểm và phổ biến nhất ở các vùng trồng lúa châu Á. Chúng có kích thước nhỏ (khoảng 3–4 mm), màu nâu sẫm, thường sinh sống và phát triển ở phần gốc cây lúa, đặc biệt trong môi trường ẩm ướt, rậm rạp. Rầy nâu gây hại bằng cách chích hút nhựa ở thân và bẹ lúa, làm cây bị vàng úa, còi cọc, nặng hơn là gây hiện tượng 'cháy rầy' – lúa bị chết hàng loạt thành từng đám. Ngoài ra, Nilaparvata lugens còn là môi giới truyền bệnh virus lùn xoắn lá, khiến thiệt hại càng nghiêm trọng. Mật độ rầy cao thường xảy ra vào cuối vụ, khi điều kiện khí hậu thuận lợi và ruộng không được quản lý tốt.",
    "Red Mite": "Red Mite (bọ đỏ) là một loài ve nhỏ thuộc nhóm nhện hại cây trồng, có kích thước rất nhỏ (khoảng 0.3 – 0.5 mm), cơ thể có màu đỏ hoặc đỏ cam đặc trưng, thường rất khó quan sát bằng mắt thường. Loài này phát triển mạnh trong điều kiện thời tiết nắng nóng, khô hanh, đặc biệt vào mùa khô hoặc giai đoạn giao mùa. Chúng thường cư trú ở mặt dưới của lá cây – nơi có điều kiện ẩn nấp lý tưởng và ít chịu tác động của môi trường bên ngoài. Bọ đỏ gây hại chủ yếu bằng cách chích hút dịch từ tế bào lá, khiến lá cây mất màu xanh, chuyển dần sang màu vàng nhạt hoặc xám bạc, xuất hiện các vết khô cháy loang lổ. Lá bị hại nặng sẽ nhanh chóng rụng sớm, làm giảm khả năng quang hợp, ảnh hưởng nghiêm trọng đến quá trình sinh trưởng, phát triển và năng suất của cây. Khi mật độ cao, bọ đỏ còn có thể làm cây còi cọc, khô héo, thậm chí chết cây non. Các cây trồng thường bị ảnh hưởng bao gồm: lúa, đậu, ớt, dưa, cam quýt, xoài và nhiều loại cây công nghiệp như chè, bông, cao su…",
    "Squash Bug": "Squash Bug (bọ xít bí) là loài côn trùng chuyên gây hại trên các cây họ bầu bí như bí đỏ, bí ngòi, bí xanh và dưa leo. Chúng có thân hình dẹt, dài khoảng 1.5 cm, màu nâu xám, dễ lẩn trốn dưới tán lá hoặc gốc cây. Squash Bug gây hại bằng cách chích hút nhựa từ thân, lá và quả non, làm lá héo rũ, chuyển màu nâu và chết dần, đặc biệt ở cây non có thể khiến cả cây bị chết sớm. Ngoài gây héo lá, chúng còn là môi giới truyền một số bệnh vi khuẩn nguy hiểm, làm cây trồng dễ bị nhiễm bệnh thứ cấp. Bọ xít bí phát triển mạnh vào mùa hè, sinh sản nhanh, trứng thường được đẻ ở mặt dưới lá theo từng cụm. Khi nở, ấu trùng sẽ tiếp tục chích hút gây hại."
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "Không có ảnh được tải lên!"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Tên file không hợp lệ!"}), 400

    # Tạo tên file duy nhất
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Đọc ảnh và phát hiện côn trùng
    img = cv2.imread(file_path)
    model = YOLO("bestv11vip.pt")  # Sử dụng mô hình cố định
    results = model(img)
    boxes = results[0].boxes

    # Nếu không phát hiện gì thì tạo ảnh đen
    if boxes is None or len(boxes) == 0:
        black_img = np.zeros_like(img)
        result_path = os.path.join(RESULT_FOLDER, filename)
        cv2.imwrite(result_path, black_img)
        return jsonify({
            "image_url": "/" + result_path,
            "original_url": "/" + file_path,
            "counts": {},
            "message": "Không phát hiện thấy côn trùng."
        })

    # Đếm và vẽ box
    labels = [model.names[int(box.cls)] for box in boxes]
    count_result = Counter(labels)

    insect_details = {label: insect_info.get(label, "Không có thông tin") for label in labels}

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = model.names[int(box.cls)]
        confidence = round(float(box.conf[0]), 2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"{label} ({confidence})", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    result_path = os.path.join(RESULT_FOLDER, filename)
    cv2.imwrite(result_path, img)

    return jsonify({
        "image_url": "/" + result_path,
        "original_url": "/" + file_path,
        "counts": count_result,
        "insect_details": insect_details
    })

@app.route("/upload_video", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "Không có video được tải lên!"}), 400

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "Tên file không hợp lệ!"}), 400

    # Tạo tên file duy nhất
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Xử lý video
    cap = cv2.VideoCapture(file_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    result_path = os.path.join(RESULT_FOLDER, filename)
    out = cv2.VideoWriter(result_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    detected_labels = set()  # Sử dụng set để lưu trữ các loài duy nhất

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        boxes = results[0].boxes

        if boxes is not None and len(boxes) > 0:
            labels = {model.names[int(box.cls)] for box in boxes}
            detected_labels.update(labels)  # Cập nhật các loài phát hiện

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model.names[int(box.cls)]
                confidence = round(float(box.conf[0]), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ({confidence})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        out.write(frame)

    cap.release()
    out.release()

    # Chuyển đổi set thành Counter để trả về
    total_counts = Counter(detected_labels)

    return jsonify({
        "video_url": "/" + result_path,
        "original_url": "/" + file_path,
        "counts": total_counts,
        "insect_details": {label: insect_info.get(label, "Không có thông tin") for label in detected_labels}
    })

if __name__ == "__main__":
    app.run(debug=True)