# Xuất CSV từ kết quả query nhập tay

Chỉ xuất khi người dùng yêu cầu CSV. Query gõ tay không cần có file hay ID: agent tự cấp một ID chưa dùng như `q001-kis`, `q002-qa`, `q003-trake`, giữ nguyên query trong hồ sơ và tạo JSON nội bộ cho exporter. Mỗi query xuất một file `<query_id>.csv`; lượt yêu cầu “xuất kết quả vừa tìm” dùng lại hồ sơ hiện tại. Nếu đầu vào thực sự là file query, có thể dùng stem của file.

Mỗi file tối đa 100 dòng dự đoán. Quy cách tham khảo từ `query_types.docx`: không header, dấu phẩy phân tách, UTF-8. Không cần mở DOCX để xuất. CSV writer quote chuỗi đúng chuẩn (kể cả đáp án là số); không nối tay bằng dấu phẩy.

| Loại | Cột |
| --- | --- |
| KIS | tên video, frame gốc |
| Q&A (`qa`) | tên video, frame gốc, đáp án tối đa 100 ký tự |
| TRAKE | tên video, frame gốc E1, ..., frame gốc EN |

Quy định tài liệu gọi cột TRAKE là Frame ID; trong pipeline này cần quy đổi chỉ số kho ảnh sang chỉ số video bằng map, giống phân biệt `keyframeId`/`frameIdx` ở frontend. Nếu một bộ dữ liệu mới quy định hệ ID khác, đối chiếu hướng dẫn bộ đó trước khi xuất.

## Dữ liệu đầu vào của exporter

Agent tạo JSON sau khi xem bằng chứng; người dùng chỉ cần nhập query và yêu cầu CSV. Các ID dưới đây chỉ minh họa, không phải đáp án đã tìm được:

```json
{
  "query_id": "query-example-qa",
  "type": "qa",
  "candidates": [
    {
      "video_name": "L00_V000",
      "keyframe_ids": [12],
      "answer": "5",
      "verified": true,
      "evidence": ["Đường dẫn ảnh thật đã xem và mô tả phần ảnh hỗ trợ đáp án"]
    }
  ]
}
```

`verified` là xác nhận của agent sau khi kiểm tra, không phải kết quả mà script tự suy ra. Script kiểm tra cấu trúc, không chấm được ngữ nghĩa hay chứng minh đường dẫn ảnh là bằng chứng đúng. Không đặt `true` chỉ vì search score cao.

- KIS: `type: "kis"`, một keyframe mỗi candidate, không cần answer.
- QA: một keyframe và answer chuỗi; số cũng ghi dạng `"5"`, không JSON number.
- TRAKE: `type: "trake"`, trường top-level `event_count: N`, mỗi candidate có đúng N `keyframe_ids` theo thứ tự E1..EN trong cùng video.
- Agent chọn và xếp hạng các candidate trước khi export. Exporter không tự chọn top result, không lấp đủ 100 dòng, không bỏ qua dòng lỗi.

Map local `maps/L00_V000.csv` cần header tường minh, ví dụ:

```csv
id,frame_idx,pts_time,fps
12,3450,138.0,25
```

Đây là dữ liệu minh họa. Khi chạy thật, dùng map đúng video/bộ dữ liệu. Hỗ trợ cột keyframe `keyframe_id`, `keyframeid`, `id`, `n`; cột frame `frame_idx`, `frameidx`, `frame_id`. Nếu nhiều cột ID, chỉ định `--map-id-column n` sau khi xác minh nghĩa của nó. Không suy ID từ số thứ tự dòng. Nếu map không có header, chuẩn hóa một bản local với tên cột đã xác minh; không sửa dữ liệu gốc.

```powershell
python .agents/skills/aic-video-retrieval/scripts/export_submission.py work/query-example-qa/reviewed.json --map-dir work/maps --output-dir work/submissions
```

Kết quả ví dụ: `"L00_V000",3450,"5"`. Dấu quote quanh tên video là CSV hợp lệ, không trở thành một phần của giá trị cột.

Nếu đã căn chỉnh chính xác trên video gốc (ví dụ mốc tiếp xúc kẻng giữa hai keyframe), dùng `frame_indices: [3450]` **thay** `keyframe_ids`, kèm `frame_source` mô tả nguồn chỉ số video và cách xác minh; không cần map trong chế độ này. Không dùng chế độ này để bypass map cho ID của search API.

```json
{
  "query_id": "query-example-trake",
  "type": "trake",
  "event_count": 3,
  "candidates": [{
    "video_name": "L00_V000",
    "frame_indices": [3450,3620,4010],
    "frame_source": "Chỉ số frame từ video gốc đã kiểm tra; mô tả cụ thể nguồn tại đây",
    "verified": true,
    "evidence": ["Bằng chứng E1, E2, E3 và kiểm tra frame trước mỗi mốc"]
  }]
}
```

Exporter từ chối: thiếu map/ID, số âm/số lẻ, answer rỗng/>100 ký tự, sai số events, chuỗi không tăng nghiêm ngặt, dòng trùng, >100 dòng, candidate chưa xác minh. Không tự sort event, không cắt answer. Không ghi đè CSV có sẵn trừ khi có `--force`. Bằng chứng giữ trong JSON ngoài file CSV. Chỉ nộp file lên hệ thống thi nếu người dùng yêu cầu riêng việc nộp.
