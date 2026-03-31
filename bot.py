import os
import random
import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Config ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_IDS = [
    int(x.strip())
    for x in os.environ.get("CHAT_IDS", "").split(",")
    if x.strip()
]
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Ho_Chi_Minh")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

VN_TZ = pytz.timezone(TIMEZONE)

# Ngày Tết Nguyên Đán (Mùng 1 Tết) các năm
TET_DATES = {
    2025: datetime(2025, 1, 29, tzinfo=pytz.UTC),
    2026: datetime(2026, 2, 17, tzinfo=pytz.UTC),
    2027: datetime(2027, 2, 6,  tzinfo=pytz.UTC),
    2028: datetime(2028, 1, 26, tzinfo=pytz.UTC),
    2029: datetime(2029, 2, 13, tzinfo=pytz.UTC),
}

ZODIAC = {
    2025: "Ất Tỵ 🐍",
    2026: "Bính Ngọ 🐴",
    2027: "Đinh Mùi 🐑",
    2028: "Mậu Thân 🐒",
    2029: "Kỷ Dậu 🐓",
}

# 17 mẫu tin nhắn hài hước xoay vòng
TEMPLATES = [
    (
        "🎊 *THÔNG BÁO KHẨN CẤP!*\n"
        "Còn *{mondays} thứ Hai* nữa là Tết {zodiac}!\n"
        "_Bộ não thứ Hai của bạn đang dần thoát xác..._"
    ),
    (
        "📅 *Điểm danh thứ Hai!*\n"
        "Chỉ còn *{mondays} thứ Hai* nữa thôi!\n"
        "Tết {zodiac} đang đến gần!\n"
        "_Mặt bạn đang sáng dần lên khi đọc cái này... phải không?_ 😏"
    ),
    (
        "⏰ TICK TOCK TICK TOCK!\n"
        "Còn *{mondays} thứ Hai* nữa là Tết {zodiac}!\n"
        "_Ngày được nghỉ ăn bánh chưng đang lại gần~_ 🍱"
    ),
    (
        "🐉 *TIN VUI GIỮA THỨ HAI U ÁM!*\n"
        "Chỉ còn *{mondays} tuần* nữa là Tết {zodiac}!\n"
        "_Hãy tiếp tục chiến đấu, chiến binh văn phòng!_ 💪"
    ),
    (
        "😭 Ôi thứ Hai ơi...\n"
        "Nhưng đừng buồn! Chỉ còn *{mondays} thứ Hai* nữa!\n"
        "Tết {zodiac} sẽ giải cứu bạn!\n"
        "_Phong bì lì xì đang chờ đợi bạn..._ 🧧"
    ),
    (
        "🚀 *ĐẾM NGƯỢC TẾT - MISSION IMPOSSIBLE!*\n"
        "Mission: Sống sót qua *{mondays} thứ Hai* còn lại!\n"
        "Phần thưởng: Tết {zodiac} 🎉\n"
        "_Bạn có thể làm được! Có lẽ vậy..._"
    ),
    (
        "☕ Thứ Hai, cà phê và đếm ngược!\n"
        "Còn đúng *{mondays} thứ Hai* nữa là Tết!\n"
        "{zodiac} đang ở đầu kia đường hầm!\n"
        "_Ánh sáng đó là Tết hay là tàu hoả nhỉ?_ 🚂"
    ),
    (
        "🎯 *WEEKLY REPORT - BỘ PHẬN TẾT:*\n"
        "✅ Vừa sống sót qua 1 thứ Hai\n"
        "⏳ Còn lại: *{mondays} thứ Hai*\n"
        "🎊 Mục tiêu: Tết {zodiac}\n"
        "_Tiến độ: Chậm nhưng chắc!_"
    ),
    (
        "😤 *MONDAY WARRIOR MODE ACTIVATED!*\n"
        "Thứ Hai không thể đánh bại tôi!\n"
        "Chỉ còn *{mondays} cái thứ Hai* nữa thôi!\n"
        "Tết {zodiac} ta sẽ thắng! 💪\n"
        "_Plot twist: Tết xong lại thứ Hai... 😭_"
    ),
    (
        "🎪 *CHƯƠNG TRÌNH ĐẾM NGƯỢC TẾT!*\n"
        "🎬 Hôm nay: Thứ Hai khổ sai\n"
        "📺 Tập tiếp theo: *{mondays} thứ Hai* nữa\n"
        "🏆 Finale: Tết {zodiac} 🎊\n"
        "_Vỗ tay nào! Hoặc khóc. Tùy bạn._"
    ),
    (
        "🌸 Xuân về đang kề bên!\n"
        "Chỉ cần vượt qua *{mondays} thứ Hai* nữa!\n"
        "Tết {zodiac} rồi hoa đào nở! 🌺\n"
        "_Và rồi lại đi làm... nhưng thôi kệ!_"
    ),
    (
        "💼 *MEETING KHẨN - CHỦ ĐỀ: TẾT*\n"
        "📋 Agenda: Đếm ngược Tết\n"
        "📊 Kết quả: Còn *{mondays} thứ Hai*\n"
        "✅ Kết luận: Tết {zodiac} sắp đến!\n"
        "_Cuộc họp này có ích hơn 90% cuộc họp khác_ 😂"
    ),
    (
        "🍜 Phở thứ Hai sang chảnh!\n"
        "Ăn xong nhớ: còn *{mondays} thứ Hai* nữa là Tết!\n"
        "{zodiac} - Năm của sự phát đạt! 🤑\n"
        "_Và của bánh chưng không giới hạn!_"
    ),
    (
        "🎮 *GAME PROGRESS - CUỘC ĐỜI:*\n"
        "🗺️ Map: Văn Phòng Việt Nam\n"
        "📍 Location: Thứ Hai\n"
        "⏳ Quest còn lại: *{mondays} thứ Hai*\n"
        "🏆 Boss cuối: Tết {zodiac}!\n"
        "_Loot: Lì xì 🧧 và tăng cân 🍖_"
    ),
    (
        "📣 *BREAKING NEWS - VTV ĐẶC BIỆT!*\n"
        "Một người bình thường vừa phát hiện:\n"
        "Chỉ còn *{mondays} thứ Hai* nữa là Tết {zodiac}!\n"
        "_Phóng viên hiện trường: Gương mặt bừng sáng hẳn ra!_ 😍"
    ),
    (
        "🌙 *THỨ HAI - NGÀY KIÊNG KỴ DÂN GIAN:*\n"
        "Theo tục lệ: né thứ Hai tối đa 😅\n"
        "Nhưng chỉ cần chịu thêm *{mondays} cái* nữa!\n"
        "Sau đó: Tết {zodiac} 🎊\n"
        "_Câu thần chú: Còn {mondays} thứ Hai... còn {mondays} thứ Hai..._"
    ),
    (
        "🦸 *SIÊU ANH HÙNG KHÔNG TÊN:*\n"
        "Khả năng: Sống sót qua mọi thứ Hai\n"
        "Thành tích: Đã qua vô số thứ Hai\n"
        "Nhiệm vụ tiếp theo: *{mondays} thứ Hai* rồi Tết {zodiac}!\n"
        "_Không có áo choàng nhưng có cà phê!_ ☕"
    ),
]


def get_next_tet():
    """Trả về ngày Tết tiếp theo và zodiac tương ứng."""
    now = datetime.now(VN_TZ)
    for year in sorted(TET_DATES.keys()):
        tet_dt = TET_DATES[year].astimezone(VN_TZ)
        if tet_dt > now:
            return tet_dt, ZODIAC.get(year, str(year))
    # Fallback
    last_year = max(TET_DATES.keys())
    return TET_DATES[last_year].astimezone(VN_TZ), ZODIAC.get(last_year, "")


def count_mondays_until_tet():
    """Đếm số thứ Hai còn lại đến Tết."""
    now = datetime.now(VN_TZ)
    tet_date, zodiac = get_next_tet()
    days_until = (tet_date.date() - now.date()).days

    count = 0
    current = now.date() + timedelta(days=1)  # bắt đầu từ ngày mai
    while current <= tet_date.date():
        if current.weekday() == 0:  # 0 = Monday
            count += 1
        current += timedelta(days=1)

    return count, days_until, zodiac


def build_countdown_message():
    mondays, days, zodiac = count_mondays_until_tet()
    template = random.choice(TEMPLATES)
    message = template.format(mondays=mondays, zodiac=zodiac)
    message += f"\n\n📊 _({days} ngày nữa đến Tết)_"
    return message


async def send_monday_message(app: Application):
    message = build_countdown_message()
    for chat_id in CHAT_IDS:
        try:
            await app.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
            )
            logger.info(f"Sent Monday message to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send to {chat_id}: {e}")


# --- Command handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mondays, days, zodiac = count_mondays_until_tet()
    text = (
        "🎊 *Bot Đếm Ngược Tết Âm Lịch!*\n\n"
        f"Còn *{mondays} thứ Hai* nữa là Tết {zodiac}!\n"
        f"_{days} ngày nữa thôi!_\n\n"
        "📋 *Lệnh có sẵn:*\n"
        "/start — Thông tin bot\n"
        "/conbaonhieu — Đếm ngược Tết ngay bây giờ\n"
        "/mychatid — Xem Chat ID của bạn\n\n"
        "_Bot sẽ tự động nhắc bạn mỗi thứ Hai lúc 8h sáng!_ ⏰"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def conbaonhieu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = build_countdown_message()
    await update.message.reply_text(message, parse_mode="Markdown")


async def mychatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    text = (
        "📍 *Thông tin Chat của bạn:*\n\n"
        f"👤 User ID: `{user.id}`\n"
        f"💬 Chat ID: `{chat.id}`\n"
        f"📝 Chat Type: `{chat.type}`\n"
    )
    if chat.title:
        text += f"🏷️ Chat Title: `{chat.title}`\n"
    text += (
        "\n_Copy Chat ID này vào biến môi trường CHAT_IDS "
        "để bot gửi tin nhắn cho bạn!_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN chưa được set!")
    if not CHAT_IDS:
        logger.warning("CHAT_IDS chưa được set — bot sẽ không tự gửi tin nhắn!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("conbaonhieu", conbaonhieu))
    app.add_handler(CommandHandler("mychatid", mychatid))

    scheduler = AsyncIOScheduler(timezone=VN_TZ)
    scheduler.add_job(
        send_monday_message,
        "cron",
        day_of_week="mon",
        hour=8,
        minute=0,
        args=[app],
        id="monday_tet_countdown",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — sẽ gửi tin lúc thứ Hai 8h sáng VN!")

    logger.info("Bot đang chạy... Ctrl+C để dừng.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
