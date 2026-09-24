# Hợp đồng API AIC_BE

Đối chiếu source và OpenAPI local ngày 2026-09-23. Root workspace là `D:/AIC/BE`; các đường dẫn source dưới đây tính từ root. Đọc OpenAPI của deployment trước khi dùng nếu code đã thay đổi. Không import `src.main` chỉ để xem schema vì import/startup có thể nạp model lớn.

## Request

Các endpoint sau dùng POST JSON. Script nhận tên operation ở cột trái và chuyển tới route chính xác. Ghi payload vào file UTF-8 để tránh lỗi quote/tiếng Việt trên PowerShell; có thể dùng stdin khi môi trường đã cấu hình UTF-8.

| Operation | Route | Payload ví dụ |
| --- | --- | --- |
| `semantic` | `/search` | `{"query":"lions resting on wooden platforms at a zoo","topk":30,"model":"siglip","language":"en","semantic_method":"baseline"}` |
| `fuse` | `/fuse_search` | `{"query":["people exercising in a row","three red hats"],"topk":30,"model":"siglip","language":"en","gpt_split":false,"semantic_method":"facr"}` |
| `temporal` | `/temporal_search` | `{"query":["a map showing dams","aerial view of a dam","close view of a dam in rain"],"topk":30,"model":"siglip","language":"en","gpt_split":false,"temporal_method":"huytemporal"}` |
| `ocr` | `/search_OCR` | `{"query":"London Zoo","topk":30,"mode":"elastic"}` |
| `asr` | `/search_ASR` | `{"query":"remember","topk":30,"mode":"elastic"}` |
| `conversation` | `/search_cir` | `{"reference":{"video_name":"L00_V000","frame_index":12},"edit_text":"three red hats","remove_text":"blue hats","top_k":30,"edit_strength":0.95,"model":"siglip","exclude_reference":true}` |
| `similar` | `/search_by_frame` | `{"video_name":"L00_V000","frame_idx":12,"topk":30,"model":"siglip"}` |
| `agent-retrieval` | `/agent_retrieval` | `{"query":"lions beside a London Zoo sign","topk":30}` |
| `translate` | `/translate` | `{"texts":["cận cảnh con đập dưới trời mưa"]}` |

Video/frame trong ví dụ chỉ minh họa schema, không phải đáp án; CIR/similar phải dùng ID từ kết quả thật.

- `video_prefix` tùy chọn trên semantic/fuse/temporal/OCR/ASR/CIR; là tiền tố tên video (`L21`, `L21_V003`), không phải regex hoặc tên nhóm thư mục `L21_a`. Muốn một video chính xác, vẫn lọc tên video bằng so sánh bằng ở kết quả.
- `SingleTextQuery.language` bắt buộc; fuse/temporal mặc định `en`. `query` của semantic/OCR/ASR là chuỗi, fuse/temporal là mảng chuỗi.
- `semantic_method`: `baseline` (mặc định), `facr`. `/fuse_search` FACR coi mỗi chuỗi là một facet đồng thời; không đảm bảo thứ tự thời gian. Không gửi FACR với ảnh data URI.
- `temporal_method`: `huytemporal` (mặc định), `wesp` (alias cùng implementation), `baseline`, `trgr`. `min_frame_dist` và `discount_rate` chỉ được route truyền xuống nhánh baseline. `gpt_split` không được dùng trong nhánh huytemporal/TRGR: agent phải tách sự kiện trước.
- Không gửi `max_frame_dist`/`metric` theo frontend: schema backend hiện không khai báo các trường này, nên chúng không cấu hình thuật toán như tên gợi ý.
- CIR dùng `top_k`, khác `topk` của các route khác; 1..1000. `edit_strength` -3..5, mặc định 0.95. Ít nhất một trong add/remove phải không rỗng, mỗi chuỗi tối đa 2000 ký tự. CIR không dịch tự động: dùng khái niệm tiếng Anh. Route này chạy trực tiếp trong AIC_BE, không cần khởi động riêng `TensorFly_CIR_Module`.
- `model: "siglip"` khớp cấu hình Compose hiện tại, nhưng không bảo đảm đã có embeddings. Các alias source khác: `ViT-H14`, `Clip-400M`, `ViT 5b`, `ViT-bigG-2B`, `vit-b32`, `vit-Med`. Chỉ chọn model đã được server nạp; không gửi `gpt-6-astra` vào trường này. CIR có thể tự fallback model mà không ghi lại trong response.
- OCR ưu tiên `elastic`. ASR hỗ trợ `elastic`, `slow`, `fast`; không thử mode tùy ý. Đây là tìm trên dữ liệu đã OCR/ASR, không phải API upload ảnh/audio để nhận dạng mới.

## Response và các giới hạn quan trọng

Semantic/OCR/ASR/CIR thường trả:

```json
{"results":[{"video_name":"L00_V000","keyframe_id":12,"score":0.73}],"query":null}
```

OCR/ASR elastic có thêm `text`; ASR có thể có ID null hoặc các ID dạng mảng trong dữ liệu/mode cũ. Không ép null thành 0; bung mảng có kiểm tra provenance trước khi ánh xạ. `score` chỉ phục vụ xếp hạng, không phải xác suất đáp án đúng.

**ID ASR cần kiểm tra riêng:** `ASR_db.py` nhập nguyên giá trị `imgs[]` thành `frame_id`, và ASR search đổi tên nó thành `keyframe_id` mà không chuyển đổi. Do đó hệ chỉ số phụ thuộc pipeline tạo transcript, không thể kết luận chỉ từ tên field. Đối chiếu dữ liệu nguồn, map và ảnh tương ứng: nếu là frame video gốc thì tìm hàng `frame_idx` tương ứng để lấy keyframe dùng xem ảnh; nếu là keyframe thì ánh xạ bình thường. Nếu cả hai cách đều có vẻ hợp lệ nhưng chưa xác định được, giữ ứng viên ASR ở mức video/text và xác minh qua visual/OCR, không tự chọn một cách. Không dùng ID ASR chưa phân loại làm anchor CIR.

Temporal trả từng ứng viên video với `matched_frames: [k1,k2,...]`, có thể có `keyframe_id` là anchor và `continuation_candidates`. Với TRAKE, dùng chuỗi `matched_frames`, không chỉ anchor. Với KIS, dùng chuỗi để xác minh rồi chọn một frame đại diện.

- Huytemporal có `retrieval_method: huytemporal_fusion` hoặc `huytemporal_unmatched_decay`; nhánh decay có thể thiếu sự kiện.
- FACR/TRGR có thể fallback: đọc `retrieval_method` và `fallback_reason` nếu hiện diện; không khẳng định đã dùng phương pháp yêu cầu khi response nói ngược lại. Không phải mọi response baseline đều có metadata này.
- TRGR `temporal_basis: scene_intervals` dùng metadata cảnh; `keyframe_order_demo` chỉ dùng thứ tự keyframe, không phải giây. Compose hiện bật fallback demo theo mặc định. `debug:true` thêm `aligned_events`, `parsed_relations`. Không dùng demo để kết luận duration/overlap hoặc mốc “đầu tiên” chính xác.
- `/agent_retrieval` trả `results[{video_name,frame_idx,score,sources}]` và `parsed_queries`. Nó phân rã visual/OCR/ASR/caption, fuse RRF với k=60, không có temporal/CIR/VQA. Source hiện có thể nuốt lỗi nhánh và trả ít/rỗng; frame 0 có thể bị bỏ do dùng toán tử `or`. Không dùng đây là nguồn duy nhất nếu cần độ bao phủ, provenance hoặc xử lý frame 0. Không coi `frame_idx` của route này là video frame gốc.

## Media và map

AIC_BE hiện không mount static media, cũng không có API đọc ảnh, transcript quanh frame hay liệt kê các model được nạp. Lấy media/map qua đường dẫn local hoặc server media đã cấu hình riêng:

- FE: `VITE_IMAGE_PATH`, `VITE_VIDEO_PATH`, `VITE_MAP_KEYFRAME`; biến thay thế `VITE_MEDIA_ROOT`, `VITE_MAP_ROOT`, `VITE_IMAGE_EXTENSION` (mặc định `.webp`). Chỉ đọc các cấu hình cần thiết; không chép credential từ `.env` vào log/tài liệu.
- Image thường `{image_root}/{video}/{keyframe_id:06d}.webp`, hoặc `{image_root}/{group}/{video}/...`; video `{video_root}/{video}.mp4`. Xác nhận layout bằng file/URL thật thay vì giả định một path luôn tồn tại.
- Map thường `{map_root}/{video}.csv`, `{map_root}/{group}/{video}.csv`, hoặc `{map_root}/{group}/video/{video}.csv`. Nhóm thường `Lxx_a`; riêng L26 phân chia a..e theo dải số video, xem `keyframes.ts` nếu cần.
- Tải map của video ứng viên vào thư mục làm việc `maps/{video}.csv`. Dùng header ID thực tế (`id`, `n`, `keyframe_id`...) và `frame_idx`, `pts_time`, `fps`. Mốc thời gian có thể hỗ trợ duyệt video; không suy frame từ một fps mặc định.
- Lấy lân cận thời gian bằng các hàng map trước/sau anchor. `/search_by_frame` là tìm tương tự toàn kho, không phải lân cận video.

## Xử lý lỗi

`doctor` đọc schema không tốn lượt gọi model. HTTP 404: kiểm tra deployment/path hoặc video; 422: sửa payload theo OpenAPI; 503 TRGR: thiếu metadata (đổi huytemporal/baseline nếu bài toán chỉ cần thứ tự và ghi phương pháp thực tế); lỗi model: chọn encoder đã load; ASR disabled/OCR index lỗi: báo modality chưa sẵn sàng, tiếp tục nhánh khác nếu đủ bằng chứng. Timeout: giảm topk/phạm vi một lần trước khi thử lại; không lặp vô hạn hoặc tự khởi động/index lại backend. Client không retry tự động.

Nguồn code: `AIC_BE/src/main.py`, `routes/models.py`, `routes/{text_img_search,fuse_search,temporal_search,OCR_search,ASR_search,frame_neighbors_search,cir_search,agent_retrieval}.py`, `helpers/agent_helper.py`, `searchers/{ft_searcher,huytemporal_searcher,trgr_searcher}.py`; `AIC_FE/final2026/src/lib/backend/{retrieval,keyframes,config}.ts`.
