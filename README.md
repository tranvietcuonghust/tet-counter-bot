# 🎊 Bot Đếm Ngược Tết Âm Lịch

Telegram bot tự động gửi tin nhắn đếm ngược số thứ Hai còn lại đến Tết Nguyên Đán, với caption hài hước xoay vòng mỗi tuần.

## Tính năng

- ⏰ Tự động gửi tin mỗi **thứ Hai lúc 8h sáng** giờ Việt Nam
- 🎭 **17 mẫu tin hài hước** xoay vòng ngẫu nhiên
- 📅 Tự động tính số thứ Hai & ngày còn lại đến Tết
- 👥 Hỗ trợ **nhiều chat** (cá nhân lẫn group)
- 🔢 Tự động nhảy sang Tết năm tiếp theo sau khi Tết qua

## Lệnh

| Lệnh | Mô tả |
|------|-------|
| `/start` | Thông tin bot và danh sách lệnh |
| `/conbaonhieu` | Xem đếm ngược Tết ngay lập tức |
| `/mychatid` | Lấy Chat ID để thêm vào cấu hình |

## Cài đặt local

```bash
pip install -r requirements.txt
```

Tạo file `config.txt`:
```
BOT_TOKEN=your_bot_token_here
CHAT_IDS=123456789,-987654321
TIMEZONE=Asia/Ho_Chi_Minh
```

Chạy bot:
```bash
python bot.py
```

## Deploy Railway

1. Push repo lên GitHub (không push `config.txt`!)
2. Tạo project mới trên [Railway](https://railway.app) từ GitHub repo
3. Vào **Variables**, thêm:
   - `BOT_TOKEN` = token từ @BotFather
   - `CHAT_IDS` = danh sách chat ID cách nhau dấu phẩy
   - `TIMEZONE` = `Asia/Ho_Chi_Minh`
4. Railway tự detect `Procfile` và deploy

## Lấy Chat ID

- Chat cá nhân: Nhắn `/mychatid` cho bot
- Group: Thêm bot vào group → nhắn `/mychatid` trong group

## Tết các năm

| Năm | Ngày Tết | Zodiac |
|-----|----------|--------|
| 2026 | 17/02/2026 | Bính Ngọ 🐴 |
| 2027 | 06/02/2027 | Đinh Mùi 🐑 |
| 2028 | 26/01/2028 | Mậu Thân 🐒 |
