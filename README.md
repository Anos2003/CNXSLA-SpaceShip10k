<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
   SpaceShip10k
</h2>
<div align="center">
    <p align="center">
        <img src="https://github.com/user-attachments/assets/ee72b1c4-04c7-4e4b-8d7a-8cf16932804a"width="170" />
        <img src="https://github.com/user-attachments/assets/1459f5bf-7fc9-4462-996d-eb1ef7633a97"width="180" />
        <img src="https://github.com/user-attachments/assets/f081d02c-b644-4e87-a40c-fcb8383c2985"width="200" />
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

---

## 1.  Giới thiệu Về Game

Đây là game được phát triển theo hướng vibe coding trong quá trình học môn Công nghệ xử lý ảnh.
Mục đích chính là nghiên cứu và làm quen với MediaPipe Hands, từ đó áp dụng vào việc điều khiển trong game bằng cử chỉ tay.

Dự án là bước nền tảng để phát triển các ứng dụng tương tác người–máy (HCI) và game điều khiển không chạm trong tương lai.

---

## 2. Bối cảnh game

Ở thiên niên kỷ thứ 12, nhân loại đã mở rộng ra khắp thiên hà.
Trong một nhiệm vụ trinh sát tại rìa không gian, tàu KX-17 bất ngờ mất kết nối với trung tâm chỉ huy.

Không lâu sau, con tàu bị một thực thể chưa xác định phát hiện và tấn công.

Không còn đường rút lui.

Người chơi phải chiến đấu, sống sót và tìm đường quay trở về tàu mẹ.

---

## 3. Demo

<img width="100%" src="https://github.com/user-attachments/assets/demo1.png"><img width="100%" src="https://github.com/user-attachments/assets/demo2.png">

*Video demo: [Xem video gameplay](https://github.com/user-attachments/assets/demo_video.mp4)*

---

## 4. Gameplay

Game sử dụng công nghệ nhận diện cử chỉ tay với MediaPipe để điều khiển tàu vũ trụ. Người chơi sử dụng webcam để điều khiển tàu bằng tay:

- **Di chuyển**: Giơ tay trái/phải để di chuyển tàu theo chiều ngang.
- **Bắn đạn**: Giơ ngón tay để bắn đạn.
- **Thay đổi vũ khí**: Nhặt các vật phẩm đặc biệt để chuyển đổi giữa các loại vũ khí (Laser, Plasma, Homing).
- **Né tránh**: Di chuyển nhanh để tránh đạn địch và thiên thạch.
- **Thu thập vật phẩm**: Bay qua các vật phẩm rơi để nâng cấp vũ khí, hồi máu hoặc kích hoạt lá chắn.

Mục tiêu: Sống sót qua các wave kẻ địch, đạt điểm cao nhất và quay trở về tàu mẹ.

---

## 5. Các loại vật phẩm

| Vật phẩm | Biểu tượng | Chức năng |
|:-----|:----------|:----------|
| Hồi máu | + | Tăng 20 HP cho tàu |
| Lá chắn | S | Kích hoạt lá chắn bảo vệ trong 5 giây |
| Nâng cấp Plasma | P | Chuyển sang vũ khí Plasma (bắn nhanh, sát thương trung bình) |
| Nâng cấp Laser | L | Chuyển sang vũ khí Laser (bắn chậm, sát thương cao) |
| Nâng cấp Homing | H | Chuyển sang vũ khí Homing (đạn tự dẫn theo kẻ địch) |
| Nâng cấp Universal | 🔄 | Chuyển đổi ngẫu nhiên giữa các loại vũ khí |
| Drone hỗ trợ | D | Kích hoạt drone bắn kèm theo |
| Burn damage | B | Thêm hiệu ứng cháy cho đạn |

---

## 6. Công nghệ sử dụng

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![PyGame](https://img.shields.io/badge/PyGame-3776AB?logo=pygame&logoColor=fff)](https://www.pygame.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=fff)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-4285F4?logo=google&logoColor=fff)](https://mediapipe.dev/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=fff)](https://numpy.org/)

---

## 7. Cấu trúc project

```
CNXSLA-SpaceShip10k/
├── main.py              # File chính chạy game
├── entities.py          # Định nghĩa các entity (Player, Enemy, Bullet, Item, etc.)
├── settings.py          # Cấu hình game (kích thước màn hình, màu sắc, etc.)
├── vision.py            # Xử lý nhận diện cử chỉ tay với MediaPipe
├── ui.py                # Giao diện người dùng (menu, HUD, etc.)
├── audio/               # Thư mục chứa nhạc nền và hiệu ứng âm thanh
├── graphics/            # Thư mục chứa hình ảnh và tài nguyên đồ họa
├── highscore.txt        # File lưu điểm cao nhất
├── stats.json           # File lưu thống kê game
├── requirements.txt     # Danh sách thư viện cần thiết
└── README.md            # Tài liệu hướng dẫn
```

---

## 8. Cài Đặt

```bash
# Clone project
git clone https://github.com/Anos2003/CNXSLA-SpaceShip10k.git

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy game
python main.py
```

**Lưu ý**: Đảm bảo máy tính có webcam để sử dụng tính năng điều khiển bằng cử chỉ tay.

---

## 9. Đóng góp


<a href="https://github.com/Anos2003/CNXSLA-SpaceShip10k/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Anos2003/CNXSLA-SpaceShip10k" />
</a>


---

## 10. Phát triển

Dự án được phát triển trong khuôn khổ môn học Công nghệ Xử lý Ảnh tại Đại học Đại Nam.

**Tác giả**: 
[Anos2003](https://github.com/Anos2003)
[Tabisan805](https://github.com/Tabisan805)

**Giảng viên hướng dẫn**: Lê Trung Hiếu - Khoa Công nghệ Thông tin - Đại học Đại Nam

---

## 11. Giấy phép

Dự án này được phát triển cho mục đích giáo dục. Vui lòng không sử dụng thương mại mà không có sự đồng ý.
