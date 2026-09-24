# Bối cảnh khởi tạo phiên AIC

Cập nhật từ phiên vận hành 2026-09-23/24 tại `D:/AIC/BE`. Đây là cấu hình và kinh nghiệm đã quan sát, không bảo đảm dịch vụ hiện vẫn chạy. Đọc một lần khi khởi tạo; không dùng đáp án của query cũ làm mặc định cho query mới.

## Khởi tạo tối thiểu

1. Giữ cấu hình người dùng nếu có; nếu không, dùng các đường dẫn dưới đây. Đọc `api-contract.md` một lần để biết payload và hệ chỉ số.
2. Nếu prompt CHƯA CÓ query và người dùng chỉ yêu cầu "Khởi tạo phiên AIC": chạy `python .agents/skills/aic-video-retrieval-gemini/scripts/aic_client.py doctor --timeout 5`, kiểm tra tồn tại thư mục media/map rồi báo ngắn sẵn sàng và chờ query.
3. **TUYỆT ĐỐI QUAN TRỌNG:** Nếu prompt ĐÃ CÓ query cần tìm: **BỎ QUA TOÀN BỘ BƯỚC BÁO SẴN SÀNG / CHỜ QUERY NÀY!** Không được báo sẵn sàng rồi dừng lại; bắt buộc dùng `run_shell_command` thực hiện truy vấn video cho query ngay lập tức và trả kết quả JSON hoàn chỉnh!

## Cấu hình đã xác minh

| Thành phần | Giá trị / trạng thái lần kiểm tra trước |
| --- | --- |
| Workspace | `D:/AIC/BE` |
| Backend | `AIC_API_BASE_URL` nếu đã đặt, mặc định `http://127.0.0.1:8000` |
| Client | `.agents/skills/aic-video-retrieval/scripts/aic_client.py`, Python 3.10+ |
| Encoder | `siglip`; semantic baseline và fuse FACR đã trả kết quả |
| Ảnh local | `D:/data_aic/keyframes/{video}/{keyframe_id:06d}.webp` |
| Map local | `D:/data_aic/map/{video}.csv` |
| Video local | `D:/data_aic/video/{video}.mp4` |
| Header map đã đọc | `id,pts_time,fps,frame_idx`; tra đúng `id`, lấy nguyên `pts_time` và `frame_idx` |
| FE fallback | `AIC_FE/final2026/.env`: `VITE_IMAGE_PATH=https://localhost:9000/keyframes`, `VITE_VIDEO_PATH=https://localhost:9000/video`, `VITE_MAP_KEYFRAME=https://localhost:9000/map`, `VITE_MEDIA_ROOT=D:\data_aic` |

Ưu tiên file local khi đã xác nhận truy cập được. Layout local đã thấy là **phẳng theo video**, không cần thử thư mục nhóm trước. URL media chỉ là cấu hình đã đọc, chưa phải bằng chứng HTTPS đang hoạt động. Không cần đọc lại toàn bộ `keyframes.ts` nếu đường dẫn trên vẫn dùng được. Đọc cấu hình mới khi người dùng đổi máy/corpus/URL hoặc file thực tế không tồn tại. Không mặc định mọi video 25 fps chỉ vì một map đã đọc ghi 25.

## Các vấn đề đã gặp và cách tránh mất thời gian

- Lượt tìm trước bị kéo dài do nhiều lượt xem ảnh rời, đổi câu semantic tương tự và rà frame sau khi đã có ứng viên mạnh. Giữ hạn của SKILL.md; xem vài ảnh đại diện trước, gom đọc độc lập, chỉ lấy lân cận từ hàng map của ứng viên mạnh nhất. Không cố đủ 5 kết quả khi chỉ có một ứng viên hữu ích.
- Semantic/FACR không chứng minh số lượng, màu chính xác hay phủ định “chỉ một”. Nón phối đỏ–xanh không đồng nghĩa toàn bộ nón đỏ. Người có kính bị che không đồng nghĩa không đeo kính. Ghi mâu thuẫn và chọn ứng viên tốt nhất hiện có khi hết giờ.
- Dùng `view_image` trực tiếp cho ảnh local. Đường dẫn/điểm search không thay thế việc xem ảnh. Một bảng ảnh có nhãn video/ID có thể tiết kiệm lượt nếu Pillow đã có; không cài thư viện giữa query. `sharp` từng lỗi import trong Node REPL; đừng lặp lại hướng này nếu chưa có lý do mới.
- Lấy các ID ảnh từ response/map hoặc kiểm tra file tồn tại trước; không tự tạo dải vượt số frame. Một lần tạo bảng ảnh trước đã lỗi vì yêu cầu keyframe không tồn tại.
- PowerShell đọc văn bản bằng `Get-Content -Encoding UTF8`; ghi payload thành JSON UTF-8, gọi client với `--payload`/`--output`. Không in toàn bộ source, response dài hoặc danh sách công cụ vào context khi chỉ cần trường cụ thể. Không nối các lần đọc phụ thuộc vào cuối request mạng dài.
- `exec_command` từng lỗi khởi tạo sandbox; đây là lỗi runner, không phải AIC mất kết nối. Quyền hiện tại do môi trường phiên quyết định: không hard-code escalation/bypass. Nếu lỗi lặp lại, dùng công cụ đọc file sẵn có được phép hoặc báo phần bị chặn trong hạn; không sửa môi trường để giải một query.
- Node REPL có thể mất biến sau reset; khi báo biến không tồn tại, khởi tạo lại tối thiểu. Nếu đã có công cụ xem ảnh trực tiếp thì dùng ngay, không dựng lại pipeline ảnh.
- `/search_by_frame` tìm tương tự toàn corpus, không lấy lân cận thời gian. AIC_BE không có `/vqa`, `/conversation`, `/search_rag` hoặc route static media; CIR dùng `/search_cir`. Không dò lại những route này mỗi query.
- `--timeout` của client mặc định là 90 giây và là timeout HTTP, không phải trần cả lượt. Luôn truyền tối đa 20 giây theo ngân sách còn lại; không dùng `yield_time_ms` như timeout. Mốc dừng công cụ ở giây 120 dành 30 giây cho câu trả lời.

## Giữ trạng thái giữa các query

Giữ backend/encoder, nguồn media/map thực tế, trạng thái doctor/modality và map đã tải trong phiên. Với query mới, bỏ anchor và điều kiện cũ; chỉ đọc hồ sơ cũ khi người dùng yêu cầu tiếp tục. Khi cần lưu, chọn số `work/aic/qNNN-<type>` chưa tồn tại, không ghi đè `q001-kis`. Lưu raw response ngay khi API trả; cập nhật bằng chứng và ứng viên tốt nhất khi còn ngân sách. Ghi hồ sơ phụ không được làm chậm trả lời quá 150 giây.
