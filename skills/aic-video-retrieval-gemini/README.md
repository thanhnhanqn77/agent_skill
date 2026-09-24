# Dùng AIC Video Retrieval với Google Gemini CLI

Skill này giúp Gemini Agent dùng hệ thống AIC hiện có để giải KIS, Q&A và TRAKE từ query bạn nhập trực tiếp, xác minh kết quả và tạo CSV khi được yêu cầu. Xem [mẫu prompt điền sẵn](#prompt-examples) để thêm chi tiết query và chỉ định kỹ năng/phương pháp agent cần dùng. `query_types.docx` là tài liệu tham khảo về dạng bài. Thư mục đã được đặt tại `D:\AIC\BE\.agents\skills\aic-video-retrieval-gemini` để Gemini CLI dùng trong repository này.

## 1. Thành phần và điều kiện chạy

| File | Mục đích |
| --- | --- |
| `SKILL.md` | Chỉ dẫn mà agent đọc khi skill được gọi |
| `agents/gemini.yaml` | Tên hiển thị và prompt mặc định |
| `references/session-context.md` | Cấu hình local đã xác minh, lỗi đã gặp và cách khởi tạo nhanh |
| `references/api-contract.md` | API thật, payload, response, lỗi và media/map |
| `references/query-playbook.md` | Cách giải 3 dạng bài và ánh xạ đủ 25 ví dụ |
| `references/query-types-source.md` | Nội dung text trích nguyên văn từ DOCX |
| `references/submission.md` | Hệ frame, JSON kết quả đã xác minh và quy tắc CSV |
| `scripts/aic_client.py` | Gọi API bằng JSON, kiểm tra OpenAPI |
| `scripts/export_submission.py` | Ánh xạ keyframe và xuất CSV đã kiểm tra định dạng |
| `tests/test_tools.py` | Kiểm thử offline cho công cụ |

Cần Python 3.10+, backend AIC_BE đã chạy và nạp model/index cần dùng; agent phải truy cập được ảnh/video và map keyframe của corpus. Hai script chỉ dùng thư viện chuẩn Python, không cần cài SDK OpenAI, PyTorch hay Elasticsearch client trên máy agent.

Gemini CLI (`gemini`) chạy trên Windows/Linux/macOS và tự động kích hoạt skill này khi giải các bài toán video retrieval. Model khuyến nghị: `gemini-3.8-flash` hoặc `gemini-3.8-pro`.

**VQA:** AIC_BE hiện không có route sinh đáp án. Agent dùng semantic/OCR/ASR tìm cảnh rồi xem ảnh để trả lời. **Conversation:** dùng `/search_cir` thêm/bớt khái niệm từ một ảnh anchor. Model truy xuất `siglip` trong payload và Gemini điều phối là hai cấu hình khác nhau.

## 2. Khởi động agent trong Gemini CLI

Mở workspace `D:\AIC\BE`. Gemini CLI đọc skill local tại `.agents/skills`.

### Lệnh khởi động và nạp bối cảnh một lần
```powershell
gemini --approval-mode yolo -m gemini-3.8-flash -p "Dùng `$aic-video-retrieval-gemini. Khởi tạo phiên AIC: đọc SKILL.md, references/session-context.md và references/api-contract.md."
```

Chạy lệnh này trong PowerShell để mở agent, yêu cầu đọc skill cùng cấu hình/lỗi đã biết và chờ query:

```powershell
codex -C 'D:\AIC\BE' -m gpt-6-astra 'Dùng $aic-video-retrieval. Khởi tạo phiên AIC: đọc .agents/skills/aic-video-retrieval/SKILL.md, references/session-context.md và references/api-contract.md bên trong thư mục skill. Kiểm tra kết nối và đường dẫn theo hướng dẫn khởi tạo, ghi nhớ cấu hình cùng các vấn đề đã biết. Mỗi query tối đa 150 giây; hết ngân sách trả ứng viên tốt nhất hiện có và nêu điều kiện chưa xác minh. Chưa có query: báo sẵn sàng rồi chờ tôi.'
```

Giữ **nháy đơn** quanh prompt để PowerShell không thay `$aic` thành biến môi trường/shell. Cú pháp `-C`, `-m` và prompt khởi đầu đã đối chiếu với `codex --help` trên máy ngày 2026-09-24. Lệnh giữ chính sách quyền hiện có của Codex; không tự tắt sandbox hay approval.

Backend mặc định là `http://127.0.0.1:8000`. Nếu cần server khác, đặt `$env:AIC_API_BASE_URL = 'http://dia-chi-server:8000'` trước lệnh. Agent chạy doctor một lần với timeout 5 giây; không cần chạy doctor thủ công trước rồi để agent chạy lại.

**Trong desktop app hoặc một phiên agent đã mở**, gửi prompt tương đương:

```text
Dùng $aic-video-retrieval. Khởi tạo phiên AIC.
Đọc SKILL.md, references/session-context.md và references/api-contract.md
trong D:/AIC/BE/.agents/skills/aic-video-retrieval.
Kiểm tra kết nối và nguồn media/map theo hướng dẫn, ghi nhớ cấu hình và lỗi đã biết.
Giới hạn mỗi query: 150 giây, hết ngân sách trả ứng viên tốt nhất hiện có,
kèm điều kiện chưa xác minh hoặc mâu thuẫn. Chưa có query: báo sẵn sàng rồi chờ tôi.
```

Sau thông báo sẵn sàng, chỉ cần gửi `KIS: ...`, `QA: ...`, `TRAKE: ...` hoặc một mẫu ở phần 3. Phiên giữ cấu hình kết nối, đường dẫn và trạng thái kiểm tra; không lặp việc đọc toàn bộ skill/source mỗi lần. Khởi tạo riêng diễn ra trước query; nếu gửi query ngay, phần chuẩn bị cũng tính trong 150 giây. Không cần khởi động agent mới cho từng query.

Trong phiên CLI đã mở, cũng có thể dùng `/model` để chọn model và `/status` để kiểm tra. `-m` đặt model cho phiên CLI. [Tham chiếu lệnh chính thức](https://learn.chatgpt.com/docs/developer-commands?surface=cli).

Nếu dùng desktop app, đặt URL trong prompt hoặc để agent truyền `--base-url`; biến môi trường của một terminal mới không tự truyền vào app đã mở. `AIC_API_TOKEN` chỉ cần nếu deployment có gateway Bearer riêng; route source hiện không yêu cầu token. Không lưu token vào skill.

Nếu backend ở server khác, thay URL bằng địa chỉ truy cập được từ **máy chạy agent**. `127.0.0.1` trong một runtime cloud/container trỏ về runtime đó, không tự trỏ về máy Windows. Không cần đổi backend sang GPT-6-Astra; skill điều phối đã dùng model được chọn trong Codex.

### Ngân sách mặc định: 2 phút 30 giây/query

Skill yêu cầu đo thời gian thực từ lúc bắt đầu xử lý query, tính cả suy luận, đọc tài liệu, chờ API, xem ảnh và soạn đáp án. Không reset đồng hồ khi thử cách tìm khác. Lịch làm việc mặc định:

| Mốc | Agent thực hiện |
| --- | --- |
| 0–30 giây | Truy xuất chính, khoảng 20–30 ứng viên |
| 30–90 giây | Xem ảnh đại diện, xác minh điều kiện và tra map |
| 90–105 giây | Chỉ xác minh thêm chi tiết quyết định nếu còn thời gian |
| Từ 105 giây | Không mở truy xuất mới; chốt ứng viên tốt nhất |
| Từ 120 giây | Dừng công cụ, soạn trả lời ngắn |
| Trước 150 giây | Trả kết quả hiện có, không tiếp tục tìm để đủ mọi điều kiện |

Nếu hết ngân sách, agent trả **“Kết quả tốt nhất trong giới hạn 150 giây”** cùng video/keyframe và frame gốc/timestamp đã xác minh. Kết quả chưa xem ảnh hoặc còn mâu thuẫn phải ghi rõ; điểm semantic không phải xác suất chính xác. Nếu chưa nhận được ứng viên nào do lỗi dịch vụ, agent báo tình trạng đó thay vì bịa đáp án. Khi cần tìm thêm, gửi `Tiếp tục tìm query hiện tại trong 150 giây nữa`; agent dùng lại bằng chứng đã có.

Đây là hạn bắt buộc trong quy trình agent, **không phải watchdog của Codex/runtime**. Chỉ sửa Markdown không thể bảo đảm tuyệt đối thời điểm hiển thị câu trả lời nếu nền tảng hoặc công cụ bị treo. Skill giảm rủi ro bằng timeout API tối đa 20 giây và dành 30 giây cuối cho trả lời; `yield_time_ms` và timeout HTTP không được xem như bộ ngắt toàn lượt. Các quy tắc chi tiết nằm trong [SKILL.md](SKILL.md#khởi-tạo-phiên-và-giới-hạn-150-giây).

<a id="prompt-examples"></a>

## 3. Mẫu prompt nhập query trực tiếp

Sao chép mẫu phù hợp, thay nội dung trong `[...]` bằng query và chi tiết của bạn. Xóa các dòng tùy chọn không dùng; có thể thêm bao nhiêu chi tiết cần thiết. Không cần DOCX, mã câu hỏi hay payload JSON.

### Chọn mẫu và chỉ định kỹ năng

| Bạn muốn làm gì? | Mẫu nên dùng |
| --- | --- |
| Để agent tự nhận biết yêu cầu | AUTO |
| Tìm cảnh hoặc đoạn video theo mô tả | KIS |
| Trả lời câu hỏi về nội dung trong video | QA/VQA |
| Tìm một mốc cho từng sự kiện theo thứ tự | TRAKE |
| Tìm dựa trên chữ xuất hiện trong hình | KIS + OCR |
| Tìm dựa trên lời nói trong video | KIS + ASR |
| Bổ sung chi tiết cho query đang xử lý | Hỏi tiếp |
| Tìm giống một ảnh đã chọn nhưng thay đổi đặc điểm | Conversation/CIR |

**Skill gọi bằng tên:** `$aic-video-retrieval`. Semantic, temporal, OCR, ASR, CIR và quan sát ảnh/video là các phương pháp bên trong skill này, không phải các skill độc lập để gọi bằng `$OCR` hay `$ASR`.

Trong mỗi mẫu, bạn có thể sửa dòng `Yêu cầu sử dụng:` để chỉ định phương pháp:

| Phương pháp | Khi nên yêu cầu |
| --- | --- |
| semantic | Tìm người, vật, bối cảnh, màu sắc, hành động |
| temporal | Đối chiếu các cảnh/sự kiện theo quan hệ trước–sau |
| OCR | Tìm hoặc đọc chữ, biển hiệu, nhãn, số trên hình |
| ASR | Tìm lời nói, câu thoại, tên được đọc trong video |
| CIR | Tìm theo một ảnh anchor và yêu cầu thêm/bớt đặc điểm |
| tìm ảnh tương tự | Tìm ảnh giống một keyframe đã xác định |
| quan sát ảnh/video | Xác minh chi tiết, trả lời QA, kiểm tra mốc sự kiện |

Phân biệt rõ mức yêu cầu, ví dụ:

- `Yêu cầu sử dụng: Bắt buộc dùng OCR để tìm chữ "REPAIR"; kết hợp semantic tìm bối cảnh.`
- `Yêu cầu sử dụng: Ưu tiên ASR; được kết hợp semantic nếu cần.`
- `Yêu cầu sử dụng: Chỉ dùng semantic để truy xuất; vẫn xem ảnh/video để xác minh.`
- `Yêu cầu sử dụng: Tự chọn các phương pháp phù hợp.`

Nếu phương pháp bắt buộc không khả dụng, yêu cầu agent nêu rõ phần chưa thực hiện và bằng chứng còn thiếu. Nếu muốn gọi thêm một skill khác, thêm `Kỹ năng bổ sung: Dùng $<tên-skill-đã-cài> để [nhiệm vụ cụ thể].` và thay bằng tên skill có trong phiên.

### AUTO — mẫu chung

```text
Dùng $aic-video-retrieval.
Loại: AUTO
Query:
[Dán toàn bộ mô tả hoặc câu hỏi của bạn]

Chi tiết bổ sung:
- Bối cảnh: [Địa điểm, không gian, thời điểm]
- Người/vật/hành động: [Đặc điểm cần tìm]
- Điều kiện bắt buộc: [Các chi tiết phải khớp]
- Điều kiện loại trừ: [Các chi tiết không được xuất hiện]
Yêu cầu sử dụng: [Tự chọn / bắt buộc dùng / ưu tiên phương pháp nào]
Kỹ năng bổ sung: [Tên skill đã cài và nhiệm vụ; xóa dòng nếu không cần]
Phạm vi: [Toàn bộ corpus hoặc video/nhóm video cụ thể]
Đầu ra: Trả trong chat theo đúng loại bài, kèm video/frame và bằng chứng.
Nêu rõ chi tiết chưa xác minh được.
```

Chỉ nội dung query là bắt buộc. Khi để `AUTO`, agent chọn KIS/QA/TRAKE theo đầu ra bạn cần.

Tất cả mẫu dưới đây kế thừa giới hạn **150 giây/query**; không cần thêm dòng nhắc lại. Chỉ thay đổi giới hạn khi bạn chủ động yêu cầu.

### KIS — tìm cảnh hoặc đoạn video

```text
Dùng $aic-video-retrieval.
Loại: KIS
Query:
[Mô tả cảnh hoặc đoạn video cần tìm]

Chi tiết bổ sung:
- Bối cảnh: [...]
- Người/vật: [Ngoại hình, trang phục, màu sắc, số lượng]
- Hành động: [...]
- Diễn biến trước/sau: [Nếu có chuỗi cảnh]
- Chữ hoặc lời nói liên quan: [Nếu có; giữ nguyên nội dung]
- Điều kiện bắt buộc: [...]
- Điều kiện loại trừ: [...]
Yêu cầu sử dụng: Ưu tiên semantic; dùng temporal nếu có chuỗi cảnh.
[Sửa hoặc thêm yêu cầu OCR/ASR/CIR nếu cần]
Phạm vi: [Toàn bộ corpus hoặc video/nhóm video cụ thể]
Đầu ra: Tối đa 5 kết quả trong chat, gồm video, keyframe, frame gốc/timestamp
nếu đã xác minh và các chi tiết khớp query. Nêu rõ điều kiện chưa kiểm tra được.
```

Ví dụ nội dung query: “Một người mặc áo vàng sửa xe đạp trước cửa hàng có biển REPAIR, sau đó đẩy xe ra vỉa hè.” Đây vẫn là KIS nếu bạn chỉ cần tìm đoạn phù hợp; temporal giúp kiểm tra chuỗi cảnh.

### QA/VQA — trả lời câu hỏi về video

```text
Dùng $aic-video-retrieval.
Loại: QA
Query:
[Mô tả cảnh cần tìm và câu hỏi gốc]

Chi tiết bổ sung:
- Bối cảnh để tìm cảnh: [...]
- Câu hỏi cần trả lời: [Có bao nhiêu / màu gì / tên gì / chữ hoặc số nào?]
- Người/vật cần quan sát: [...]
- Thời điểm cần xét: [Đầu tiên / cuối cùng / trước hoặc sau sự kiện nào]
- Điều kiện bắt buộc hoặc loại trừ: [...]
Yêu cầu sử dụng: Dùng semantic để tìm cảnh và quan sát ảnh/video để trả lời.
[Sửa hoặc thêm: bắt buộc OCR nếu cần đọc chữ; ASR nếu cần đối chiếu lời nói]
Phạm vi: [Toàn bộ corpus hoặc video/nhóm video cụ thể]
Đầu ra: Đáp án ngắn trước, sau đó video/frame và bằng chứng hỗ trợ.
Nếu chưa đủ bằng chứng, nói rõ chưa xác định được đáp án.
```

Ví dụ câu hỏi: “Trên nhãn chiếc hộp người đó vừa mở ghi tên thương hiệu nào?” Không điền đáp án đoán trước. VQA là bước agent xem ảnh/video để trả lời; backend hiện không có route sinh đáp án VQA riêng.

### TRAKE — xác định mốc cho từng sự kiện

```text
Dùng $aic-video-retrieval.
Loại: TRAKE
Query:
[Dán mô tả gốc của chuỗi sự kiện]

Chi tiết bổ sung:
- Bối cảnh: [...]
- E1: [Sự kiện thứ nhất và tiêu chí chọn mốc]
- E2: [Sự kiện thứ hai và tiêu chí chọn mốc]
- E3: [Sự kiện thứ ba và tiêu chí chọn mốc]
- Điều kiện bắt buộc hoặc loại trừ: [...]
Yêu cầu sử dụng: Dùng semantic tìm bối cảnh, temporal đối chiếu thứ tự,
và xem video/frame lân cận để xác minh từng mốc.
[Sửa hoặc thêm yêu cầu OCR/ASR nếu sự kiện liên quan chữ hoặc lời nói]
Phạm vi: [Toàn bộ corpus hoặc video/nhóm video cụ thể]
Đầu ra: Một video và đúng một frame gốc cho mỗi sự kiện E1..EN,
theo thứ tự đã yêu cầu, kèm bằng chứng cho từng mốc.
Với "khoảnh khắc đầu tiên", kiểm tra cả các frame trước mốc được chọn.
Nếu chỉ có keyframe thưa hoặc thiếu map/video gốc, nêu giới hạn độ chính xác.
```

Thêm/bớt các dòng E1..EN theo đúng số sự kiện trong đề; không mặc định luôn có 3 sự kiện. Ví dụ: E1 đặt cốc xuống, E2 nước bắt đầu chạm cốc, E3 nhấc cốc lên. Bối cảnh không tự trở thành một sự kiện cần trả.

### KIS + OCR — tìm theo chữ trong hình

```text
Dùng $aic-video-retrieval.
Loại: KIS
Query:
[Mô tả cảnh có chữ cần tìm]

Chi tiết bổ sung:
- Chữ cần tìm nguyên văn: [...]
- Chữ nằm ở đâu: [Biển hiệu / nhãn / màn hình / phụ đề / vị trí khác]
- Đặc điểm cảnh đi kèm: [...]
- Điều kiện bắt buộc hoặc loại trừ: [...]
Yêu cầu sử dụng: Bắt buộc dùng OCR tìm chữ; kết hợp semantic tìm bối cảnh
và xem ảnh để xác minh chữ thực tế. Giữ nguyên tên riêng, số và ngôn ngữ.
Đầu ra: Video/frame có chữ phù hợp, nội dung đọc được và bằng chứng.
```

Nếu cần trả lời “trên biển ghi gì?” thay vì tìm một cảnh có chữ đã biết, dùng mẫu QA/VQA và yêu cầu OCR.

### KIS + ASR — tìm theo lời nói

```text
Dùng $aic-video-retrieval.
Loại: KIS
Query:
[Mô tả đoạn video hoặc lời nói cần tìm]

Chi tiết bổ sung:
- Câu nói/từ khóa nguyên văn: [...]
- Ngôn ngữ lời nói: [...]
- Người nói hoặc bối cảnh hình ảnh: [...]
- Sự kiện trước/sau lời nói: [...]
- Điều kiện bắt buộc hoặc loại trừ: [...]
Yêu cầu sử dụng: Bắt buộc dùng ASR tìm lời nói; kết hợp semantic nếu cần
đối chiếu bối cảnh. Nêu rõ bằng chứng lấy từ bản chép ASR hay media đã kiểm tra.
Đầu ra: Video, đoạn lời nói khớp, timestamp/frame nếu đã xác minh,
và các chi tiết còn thiếu.
```

OCR và ASR là cách tìm bằng chứng; đầu ra vẫn có thể là KIS, QA hoặc TRAKE tùy yêu cầu.

### Hỏi tiếp — thêm chi tiết hoặc đổi phương pháp

```text
Dùng $aic-video-retrieval. Tiếp tục query hiện tại.
Chi tiết bổ sung: [...]
Giữ các điều kiện: [...]
Thay đổi/bỏ các điều kiện: [...]
Yêu cầu sử dụng: [Tiếp tục phương pháp hiện tại hoặc chỉ định phương pháp mới]
Đầu ra: Cập nhật kết quả và nêu bằng chứng đáp ứng các điều kiện mới.
```

Ví dụ: “Thêm chi tiết người đó đội mũ trắng; giữ áo vàng và biển REPAIR; bắt buộc dùng OCR để đối chiếu biển.”

### Conversation/CIR — chỉnh tìm kiếm từ ảnh anchor

```text
Dùng $aic-video-retrieval. Tiếp tục query hiện tại.
Anchor: [Kết quả thứ mấy trong lượt đã hiển thị, hoặc video + keyframe đã biết]
Query:
[Tìm cảnh tương tự ảnh anchor nhưng thay đổi điều gì]

Chi tiết bổ sung:
- Thêm đặc điểm: [...]
- Bỏ/thay đặc điểm: [...]
- Giữ nguyên đặc điểm: [...]
Yêu cầu sử dụng: Dùng CIR với đúng ảnh anchor đã chỉ định,
sau đó xem ảnh kết quả để xác minh các thay đổi.
Đầu ra: Tối đa 5 kết quả, kèm video/frame và chi tiết khớp yêu cầu mới.
```

Ví dụ: dùng ảnh kết quả thứ 2 vừa hiển thị, thay xe xanh bằng xe đỏ, giữ bối cảnh cửa hàng. CIR cần anchor thật; nếu chưa có ảnh tham chiếu, dùng mẫu KIS hoặc hỏi tiếp bằng văn bản để tìm ứng viên trước. Conversation là cách tinh chỉnh, không phải loại đầu ra thứ tư. Nếu chỉ định ID, nói rõ đó là keyframe hay frame gốc.

### Cấu hình phiên một lần

Có thể gửi phần này trước rồi dùng các mẫu query bên trên:

```text
Dùng $aic-video-retrieval cho các query tôi sẽ nhập trong phiên này.
Khởi tạo phiên AIC theo SKILL.md và references/session-context.md.
Backend: http://127.0.0.1:8000
Encoder: siglip
Media/map: Dùng cấu hình hiện có của dự án nếu truy cập được.
Yêu cầu sử dụng mặc định: Tự chọn phương pháp phù hợp, xem ảnh/video để xác minh.
Yêu cầu sử dụng ghi trong từng query sẽ được ưu tiên.
Mặc định trả kết quả trong chat kèm bằng chứng.
Giới hạn: 150 giây/query, tính cả công cụ và xác minh; hết giờ trả ứng viên tốt nhất hiện có.
Giữ rõ điều kiện đã xác minh, chưa xác minh và mâu thuẫn; không bịa đáp án.
Khi tôi nói "query mới", bỏ điều kiện và anchor của query trước, giữ cấu hình kết nối.
Khi tôi thêm chi tiết hoặc chọn một kết quả, tiếp tục query hiện tại.
```

Thay URL bằng địa chỉ backend thật nếu cần. Đây chỉ là thiết lập phiên; agent chờ query của bạn, không tự lấy câu hỏi trong tài liệu để chạy. Khi media/map chưa có hoặc không truy cập được, cung cấp thư mục/URL thật của keyframes, video và map.

### Bắt đầu query mới

Thêm dòng `Query mới.` trước bất kỳ mẫu nào ở trên. Agent giữ cấu hình phiên nhưng bỏ điều kiện và anchor của query trước.

### Yêu cầu xuất CSV

Thêm `Đầu ra: Chat và CSV trong work/submissions.` vào mẫu, hoặc gửi sau khi đã có kết quả:

```text
Dùng $aic-video-retrieval.
Xuất các kết quả đã xác minh cho query hiện tại thành CSV trong work/submissions.
Dùng frame gốc đã kiểm tra; không đưa ứng viên chưa xác minh vào file.
```

Agent tự đặt tên như `q001-kis.csv` hoặc `q002-qa.csv`; bạn không cần nhập lại query hay tạo JSON. Xuất CSV không đồng nghĩa nộp kết quả lên hệ thống thi.

## 4. Gọi công cụ thủ công để kiểm tra

Tạo payload không phụ thuộc OpenAI API:

```powershell
New-Item -ItemType Directory -Force work | Out-Null
@'
{"query":"lions resting on wooden platforms at a zoo","topk":10,"model":"siglip","language":"en","semantic_method":"baseline"}
'@ | Set-Content -LiteralPath work/semantic-request.json -Encoding utf8
python .agents/skills/aic-video-retrieval/scripts/aic_client.py semantic --payload work/semantic-request.json --output work/semantic-results.json --timeout 20
```

Đổi operation và payload theo `references/api-contract.md`. Client giữ nguyên response; raw search result chưa phải file dự đoán đã xác minh. Khi đã kiểm tra ảnh và map, tạo `reviewed.json` theo `references/submission.md`, rồi:

```powershell
python .agents/skills/aic-video-retrieval/scripts/export_submission.py work/query-p1-4-kis/reviewed.json --map-dir work/maps --output-dir work/submissions
```

Với map nằm trên server, tải đúng file `{video}.csv` vào `work/maps` trước. Exporter không tự đoán layout media/server. Không có bước gửi dữ liệu lên hệ thống thi trong các script này.

## 5. Kiểm tra và phạm vi đã xác minh

```powershell
python -B -m unittest discover -s .agents/skills/aic-video-retrieval/tests -v
```

Trong phiên tạo skill ngày 2026-09-23, 11 kiểm thử offline đã qua và cấu trúc skill đạt bộ kiểm tra `quick_validate.py`. OpenAPI local có đủ route đã mô tả; truy vấn nhỏ tới semantic, OCR, ASR, temporal, CIR và tìm ảnh tương tự đã trả dữ liệu. Đây là kiểm tra giao tiếp API, chưa phải đánh giá độ chính xác trên 25 truy vấn. VQA cần kiểm tra media thật trong lúc giải; không có chứng nhận độ chính xác hay đáp án thi kèm theo skill.

Nếu muốn mang skill sang repo khác, sao chép **cả thư mục** `aic-video-retrieval` vào `.agents/skills` của repo đó và cấu hình lại URL/media/map. Dùng skill trong một agent API tự xây cần host/tool để thực thi script và đưa ảnh vào model; việc gửi riêng `SKILL.md` không tự cấp khả năng HTTP hay đọc ổ D:. Hướng dẫn này cung cấp luồng chạy trực tiếp bằng Codex với GPT-6-Astra.
