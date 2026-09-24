# Cách giải query người dùng nhập

Áp dụng các chiến lược sau cho query mới được gõ/dán trực tiếp trong prompt. Không cần query ID hay câu trùng với ví dụ. Phân loại dựa vào đầu ra người dùng cần; chọn công cụ theo bằng chứng. Phần ví dụ ở cuối tham khảo `query_types.docx` để minh họa các tình huống, không chứa đáp án.

## KIS

Tìm chính xác cảnh đáp ứng mô tả. Dùng semantic cho cảnh tổng thể; FACR/fuse cho nhiều thuộc tính đồng thời; temporal cho nhiều cảnh nối tiếp. Những chi tiết như “chỉ một”, “ba”, màu quần/áo, hướng di chuyển, hình gấu, động tác chạm mũi chân cần được xem ảnh/video xác minh. Search score không chứng minh số lượng.

Khi có nhiều cảnh, ưu tiên một hoặc hai dấu hiệu hiếm để tìm video trước, rồi kiểm tra toàn bộ chuỗi trong video đó. Kết quả cuối KIS vẫn chỉ có một frame mỗi dòng, không chuyển định dạng sang TRAKE.

## Q&A

Tạo hai phần: `retrieval_description` (cảnh được mô tả) và `question` (đại lượng cần trả lời). Không thêm đáp án đoán vào query rồi coi kết quả truy xuất là chứng cứ xác nhận nó.

- Đọc số/chữ: mở ảnh đủ độ phân giải, crop vùng cân/biển báo/cột mốc bằng công cụ xử lý ảnh thông thường nếu cần. Phân biệt dấu thập phân, đơn vị và chữ bị che. OCR search tìm theo chữ đã biết; không có endpoint trích OCR mới từ crop trong backend này.
- Đếm: xác định vùng cần đếm, loại trừ chú giải/vật ngoài vùng, đánh dấu từng đối tượng để tránh đếm đôi. Hai lần đếm không khớp thì xem lại ảnh/crop, không lấy trung bình.
- Tên địa danh: đọc chữ trong cảnh và đối chiếu lời dẫn ASR cùng video. Không lấy một địa danh phổ biến bên ngoài corpus làm đáp án.
- Ghi lời giải và nguồn trong evidence; trường `answer` chỉ là đáp án ngắn tối đa 100 ký tự. Khi chưa đọc được, trả “chưa đủ bằng chứng” trong báo cáo, không đặt câu này vào CSV như một dự đoán.

## TRAKE

Tách chính xác E1..EN. Context mở đầu giúp xác định video nhưng không mặc nhiên là một event đầu ra. Dùng mảng event tường minh, giữ thứ tự. Tìm video ứng viên bằng context/temporal, kiểm tra từng event và mốc chuyển tiếp, sau đó ánh xạ sang frame gốc.

Ví dụ khi người dùng nhập context “cận đầu lân trắng mũi đỏ bên cờ trắng viền đỏ” và yêu cầu ba sự kiện sau, **chỉ có ba mốc cần xuất**:

1. E1: frame đầu tiên thấy đầy đủ cả hai rồng vàng đang xoay.
2. E2: frame đầu tiên chân lân đặt trên trụ sau khi hoàn tất xoay.
3. E3: frame đầu tiên dùi chạm kẻng đồng.

Cảnh “con lân đang xoay” chưa thỏa E2; dùi đang tiến gần kẻng chưa thỏa E3. Kiểm tra frame trước mốc để chứng minh chuyển tiếp. Nếu chỉ có keyframe thưa, ghi các khoảng cần xem video gốc; không gọi đó là căn chỉnh chính xác.

Payload khởi đầu (context được tìm bằng một semantic request riêng):

```json
{
  "query": [
    "Two golden dragons are fully visible while circling during a dragon dance",
    "A lion dance costume lands its feet on poles after completing a turn",
    "A striker makes contact with a brass gong during a lion dance"
  ],
  "topk": 30,
  "model": "siglip",
  "language": "en",
  "gpt_split": false,
  "temporal_method": "huytemporal"
}
```

## Phụ lục ví dụ tham khảo, không phải đầu vào bắt buộc

Phần này chỉ cần đọc khi muốn đối chiếu cách giải một tình huống tương tự. Nguồn có 20 ví dụ KIS, 4 QA và 1 TRAKE; bản trích nằm ở [query-types-source.md](query-types-source.md). Không tự giải các ví dụ này khi người dùng đang nhập một query khác.

Mọi ID bên dưới có tiền tố `query-p1-`. “VQA” ở cột xác minh nghĩa là agent quan sát media, không phải một route backend.

| ID | Truy xuất phù hợp | Bằng chứng cần xác minh |
| --- | --- | --- |
| 1-kis | semantic/fuse; CIR nếu đã có cảnh gần đúng | >5 người, động tác chạm mũi chân, đúng 1 người đeo kính, 3 nón đỏ |
| 2-kis | temporal: bản đồ → đập nhìn từ cao → cận đập mưa | Công trình xuất hiện 4 lần trên bản đồ; đủ thứ tự cảnh |
| 4-kis | semantic sư tử + OCR `London Zoo` → temporal nhân viên | Bục gỗ, biển sở thú, hai áo xanh, cân và ghi số liệu |
| 5-kis | temporal chế biến mực/đậu → lắc chảo lửa | Đĩa hành tây/ớt đỏ; cảnh cuối slow motion |
| 6-kis | temporal đá quý trong tay → mỏ lộ thiên | Trang phục hai người, động tác nâng đá, hố nhiều tầng |
| 7-kis | temporal cà rốt sao trong nồi → đĩa món ăn | Rổ lưới/đũa gỗ, thành phần đĩa, chén hồng và đũa bên phải |
| 8-kis | temporal xếp nguyên liệu → múc từ tô → đặt giữa | Hình thanh/hoa, thứ tự thao tác và vị trí đặt |
| 10-kis | semantic cắt nho, CIR thêm dây xanh/bớt sai màu | Kéo đen, dây xanh buộc cuống trước khi cắt |
| 11-kis | semantic về đích xe đạp → duyệt video | Thứ tự vàng/đen → xanh/đen → xanh/đỏ; cần chuyển động |
| 12-kis | OCR `mazut` + semantic trạm xăng → temporal | 4 tài xế (3 chờ, 1 đi trái→phải), cảnh trước đóng nắp xăng |
| 13-kis | temporal rọi đèn dưới nước → kéo lưới bình minh → ghi hình | Cùng ngữ cảnh/người; nhóm cầm máy quay xuất hiện sau |
| 14-kis | như 8-kis | Nội dung trùng ví dụ 8; giữ file kết quả riêng theo query ID |
| 18-kis | temporal bún → nước dùng/nguyên liệu → ngò → zoom xa | Cọng ngò cuối cùng, chén nước chấm có 2 miếng ớt |
| 19-kis | temporal lân đứng/xoay → nhảy → ngoạm bí → nhảy tiếp | Bí đỏ/hoa vàng và thứ tự hành động trên trụ |
| 20-kis | temporal xuống dốc mưa → đường đất cạnh ao tới nhà | 3 người, 2 dù, áo mưa người sau có hình gấu |
| 21-kis | temporal tôm trên đĩa/3 bánh mì → đầu bếp → nướng tôm | Đúng số bánh mì; tôm cắt đôi rồi nướng |
| 22-kis | ASR/OCR `remember` + semantic cô giáo áo dài hồng | Kính, áo dài, phân biệt cách dùng động từ theo thời gian |
| 23-kis | semantic/fuse giáo viên và slide → kiểm tra ảnh | Màu khung/tiêu đề, sơ đồ 3 tầng và các khối/mũi tên |
| 24-kis | ASR `lục bình` + semantic đồ đan → temporal | Lia trái→phải túi/chậu/ấm tách/túi; phụ nữ trái cầm tách sau đó |
| 25-kis | semantic/fuse hai học sinh MC sân khấu | Áo trắng/quần xanh/khăn đỏ, trống đỏ và piano phía sau |
| 3-qa | semantic cá trên cân → temporal cá bị cầm đuôi → VQA | Đọc **số cuối cùng** trên cân, không số trung gian |
| 9-qa | temporal xe vàng/đỏ/đen tới cầu → VQA/OCR | Đọc số trên biển **bên trái** cầu, không biển khác |
| 15-qa | semantic bản đồ động đất → VQA crop và đếm | Nhận ký hiệu cấp 4 từ chú giải; đếm trên bản đồ, loại chú giải |
| 17-qa | semantic sạt lở/cột mốc → OCR/ASR → temporal xe máy | Tên đèo có chứng cứ; cột mốc đỏ bị vùi, vật xanh trên xe ở cảnh cuối |
| 16-trake | context semantic + temporal 3 events + video gốc | Đúng ba mốc E1/E2/E3; các thời điểm đầu tiên, không thêm context |

## Lịch sử conversation và bằng chứng

Lưu trong hồ sơ từng query: câu gốc, loại, events/ràng buộc, anchor CIR, lượt add/remove, payload, response file, modality và ID gốc, map dùng chuyển đổi, ảnh/video đã xem, điều kiện khớp/chưa khớp. Một lượt sửa của người dùng kế thừa ràng buộc cũ còn phù hợp; không tự chuyển một ứng viên gần đúng thành đáp án xác nhận.
