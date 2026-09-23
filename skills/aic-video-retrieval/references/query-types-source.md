# N?i dung tr?ch t? query_types.docx

Ngu?n: `D:/AIC/BE/query_types.docx`, tr?ch text OOXML ng?y 2026-09-23. Gi? nguy?n n?i dung c?u h?i, k? c? l?i ch?nh t?; kh?ng ch?a ??p ?n hay x?c nh?n k?t qu?.

Các loại truy vấn

Vòng sơ tuyển bao gồm 3 dạng truy vấn chính:

Textual Known Item Search (Textual KIS): Tìm kiếm chính xác theo văn bản

Visual Question Answering (Q&A): Truy vấn dạng Hỏi-Đáp

Temporal Retrieval and Alignment of Key Events (TRAKE): Truy xuất và căn chỉnh sự kiện video theo thời gian

Các gói truy vấn

Trong vòng sơ tuyển BTC sẽ cung cấp lần lượt các gói câu truy vấn theo nhiều đợt. Với mỗi gói câu truy vấn, đội thi cần trả về kết quả tương ứng và nộp trực tiếp trên hệ thống thi này bằng tài khoản BTC đã cấp.

Với mỗi gói câu truy vấn, BTC sẽ cung cấp một danh sách các câu truy vấn trong từng file text. Ví dụ trong đợt 1, BTC cung cấp gói gồm 4 câu truy vấn query-1-kis, query-2-kis, query-3-qa, query-4-trake tương ứng với nội dung trong 4 file query-1-kis.txt, query-2-kis.txt, query-3-qa.txt, query-4-trake.txt.

Quy ước tên file truy vấn:- Hậu tố "kis": Câu truy vấn dạng Textual KIS- Hậu tố "qa": Câu truy vấn dạng Q&A- Hậu tố "trake": Câu truy vấn dạng TRAKE

Yêu cầu kết quả

Đối với mỗi câu truy vấn, đội thi cần nộp tương ứng một file .csv (comma-separated values file) với mỗi dòng tương ứng với một lần đội dự đoán kết quả. Đội thi có thể nộp file tối đa 100 dòng. Kết quả trên mỗi dòng của đội có format theo từng loại truy vấn:

1. Textual Known Item Search (Textual KIS)

Format: <Tên file video>, <Frame Idx>

Ví dụ:

L00_V000, 1234

L00_V055, 5555

L01_V028, 25300

2. Question Answering (Q&A)

Format: <Tên file video>, <Frame Idx>, <Answer>

Quy định cho Answer:- Độ dài tối đa: 100 ký tự- Có thể bằng tiếng Việt hoặc tiếng Anh- Được so sánh chính xác về mặt ngữ nghĩa với đáp án

Ví dụ:

L01_V028, 3450, "5"

L02_V011, 1200, "Năm người"

L03_V005, 2800, "Màu đỏ"

3. Temporal Retrieval and Alignment of Key Events (TRAKE)

Format: <Tên file video>, <Frame ID_1>, <Frame ID_2>, ..., <Frame ID_N>

Trong đó:- Frame ID_1, Frame ID_2, ..., Frame ID_N là các keyframe tương ứng với N events trong chuỗi sự kiện- Số lượng Frame ID phải khớp với số events được yêu cầu trong truy vấn- Thứ tự các Frame ID phải tuân theo thứ tự thời gian của các events

Ví dụ (chuỗi 4 events):

L10_V001, 1200, 1850, 2100, 2450

L10_V001, 1180, 1820, 2080, 2420

L11_V003, 5100, 5700, 6200, 6800

Ví dụ:Textual Known Item Search (KIS)

Câu query-p1-1-kis

Cảnh quay một nhóm hơn 5 người xếp thành hàng tập thể dục, cùng thực hiện động tác hai tay chạm mũi chân. Trong nhóm chỉ có một người đeo kính và ba người đội nón có màu đỏ.

Câu query-p1-2-kis

Đoạn phim bắt đầu bằng một bản đồ, trên đó một loại công trình thủy lợi lần lượt xuất hiện bốn lần. Sau đó chuyển sang cảnh một con đập được quay từ trên cao, tiếp đến là cảnh cận con đập dưới trời mưa.

Câu query-p1-4-kis

Một đàn sư tử đang nghỉ ngơi và leo trèo trên các bục gỗ trong khu nuôi dưỡng, phía trước có bảng thông tin của London Zoo phục vụ công tác theo dõi và bảo tồn động vật.. Sau đó có cảnh hai nhân viên mặc áo xanh lá đang cân và ghi nhận số liệu của một con vật trong khuôn viên sở thú.

Câu query-p1-5-kis

Đoạn clip bắt đầu bằng việc đậu hà lan được bỏ vào với mực đang được xào trên chảo, bên cạnh là đĩa hành tây và ớt đỏ thái lát chuẩn bị cho vào món ăn. Đoạn clip kết thúc với khung quay chậm (slow motion) cảnh lắc chảo trên bếp lửa.

Câu query-p1-6-kis

Mẩu tin bắt đầu với hình ảnh nột người đàn ông mặc vest xanh đậm, sơ mi trắng và cà vạt, đang ngồi trên một chiếc ghế lớn. Ông cầm bằng hai tay một khối đá quý thô khá lớn, đưa lên gần mặt để quan sát.Bên phải là một phụ nữ mặc trang phục công sở màu đen và khăn trùm đầu màu hồng tím, đang đứng cạnh và mỉm cười. Tiếp theo có hình ảnh toàn cảnh từ trên cao của một mỏ đá quý lộ thiên quy mô lớn với hố khai thác sâu nhiều tầng và hệ thống đường vận chuyển bao quanh.

Câu query-p1-7-kis

Đoạn clip bắt đầu bằng cảnh cà rốt cắt hình ngôi sao đang được luộc trong nồi nước sôi, đặt trong rổ lưới kim loại và được đảo bằng đôi đũa gỗ.Đoạn clip kết thúc bằng hình ảnh đĩa rau củ luộc và đồ chiên được trình bày đẹp mắt, gồm đậu bắp, súp lơ, cà rốt hình ngôi sao, bí xanh, chén nước chấm màu hồng ở giữa và đôi đũa màu hồng nhạt đặt bên phải

Câu query-p1-8-kis

Người đầu bếp lần lượt đặt các miếng nguyên liệu dạng thanh và những lát cắt hình hoa vào một đĩa đang được hấp trong nồi.Các nguyên liệu được dùng đũa sắp xếp xen kẽ xung quanh phần thức ăn đã có sẵn trên đĩa.Sau đó, đầu bếp dùng muỗng lấy thêm một loại nguyên liệu mềm từ tô thủy tinh.Phần nguyên liệu này được đặt vào giữa đĩa, xung quanh là các miếng dạng thanh và hình hoa đã được sắp xếp trước đó.

Câu query-p1-10-kis

Hành động cắt chùm nho bằng kéo từ giàn nho bằng một chiếc kéo màu đen. Có thể thấy có một sợi dây màu xanh dương được buộc vào cuống của chùm nho này trước khi nó được cắt.

Câu query-p1-11-kis

Cảnh quay chậm tại vị trí vạch đích của cuộc đua xe đạp. Góc máy sát mặt đường bắt trọn khoảnh khắc về đích theo thứ tự nhất, nhì, ba lần lượt là 1 tay đua áo vàng quần đen, 1 tay đua áo xanh dương quần đen và 1 tay đua áo xanh dương quần đỏ

Câu query-p1-12-kis

Có thể thấy trong cảnh quay có 4 tài xế xe ôm công nghệ trong trạm xăng, trong đó 3 người đứng đợi còn 1 người lái xe từ trái sang phải khung hình. Trước đó là cảnh một người đậy nắp bình xăng xe máy của họ. Có thông tin về giá dầu mazut được hiển thị trong khung hình.

Câu query-p1-13-kis

Một người đứng dưới nước và rọi đèn. Tiếp theo là cảnh người này kéo lưới cá lúc bình minh, sau đó được một nhóm người khác tiến đến dùng máy quay ghi hình.

Câu query-p1-14-kis

Người đầu bếp lần lượt đặt các miếng nguyên liệu dạng thanh và những lát cắt hình hoa vào một đĩa đang được hấp trong nồi.Các nguyên liệu được dùng đũa sắp xếp xen kẽ xung quanh phần thức ăn đã có sẵn trên đĩa.Sau đó, đầu bếp dùng muỗng lấy thêm một loại nguyên liệu mềm từ tô thủy tinh.Phần nguyên liệu này được đặt vào giữa đĩa, xung quanh là các miếng dạng thanh và hình hoa đã được sắp xếp trước đó.

Câu query-p1-18-kis

Cảnh quay cho thấy hành động trình bày món ăn sau khi hoàn thành giai đoạn chế biến. Bún được cho đầu tiên vào một chén rỗng, sau đó đầu bếp lần lượt cho từng vá nước dùng cùng các nguyên liệu như thịt gà, cà rốt, sả, nấm mèo vào chén bún, và kết thúc bằng việc thả một cọng ngò lên trên cùng. Cảnh quay tiếp theo là cảnh zoom xa dần chén bún, ta thấy bên cạnh chén bún còn có 1 chén nước chấm nhỏ với 2 miếng ớt.

Câu query-p1-19-kis

Con lân do hai người điều khiển đang đứng thẳng và xoay vòng trên đỉnh cột. Sau vài giây nghỉ, con lân bất ngờ nhảy qua hai chiếc cột kế bên, chúi đầu xuống ngoạm lấy quả bí đỏ kèm bông hoa màu vàng. Cảnh quay kết thúc khi con lân tiếp tục nhảy sang các cột tiếp theo.

Câu query-p1-20-kis

Ba người đang đi bộ xuống một con dốc trong cơn mưa, có 2 người cầm dù, trong đó người cầm dù đi sau lại mặc một chiếc áo mưa có in hình con gấu ở sau lưng. Sau đó ta thấy nhiều người đang cùng nhau bước về hướng một căn nhà thông qua một con đường đất, bên cạnh là một cái ao.

Câu query-p1-21-kis

Cảnh quay bắt đầu bằng cảnh những con tôm đã được lột vỏ và nấu chín đang nằm trên dĩa, phía sau là người đầu bếp đang đặt 3 ổ bánh mì lên bàn. Sau đó là cảnh quay các đầu bếp, có người thì trang trí món ăn, có người thì chế biến món ăn. Những con tôm được cắt làm đôi và được nướng trên bếp.

Câu query-p1-22-kis

Người phụ nữ mặc áo dài màu hồng, đeo kính đang giảng giải về các trường hợp sử dụng khác nhau của động từ 'remember' dựa trên mốc thời gian của hành động được nhắc tới.

Câu query-p1-23-kis

Hình ảnh giáo viên nam mặc sơ mi trắng, thắt cà vạt tối màu, nổi bật trên phông nền xanh dương đậm có hoa văn mờ.

Slide bài giảng Nền trắng với khung viền màu hồng tím, phía trên có thanh tiêu đề xanh dương chứa họa tiết địa cầu và mũi tên vàng/xanh ngọc. Bên dưới là sơ đồ 3 tầng được liên kết bởi các mũi tên xanh ngọc trỏ xuống:

Tầng 1: 2 khối hộp được bao bởi 1 khối hộp cam.

Tầng 2: 1 khối hộp lớn màu xanh dương đậm ở chính giữa.

Tầng 3: 2 khối hộp được bao bởi 1 khối hộp xanh lá cây.

Câu query-p1-24-kis

Đoạn clip được cắt từ một phóng sự về một nhóm các nghệ nhân làm nghề đan lát các sản phẩm thủ công từ cây lục bình. Đầu tiên là một cảnh lia cam duy nhất từ trái sang phải, theo thứ tự ta thấy 4 sản phẩm: túi xách, chậu hoa, bộ ấm tách trà và túi xách. Ngay sau cảnh này, người phụ nữ bên trái lấy một tách trà trong bộ ấm tách và nâng niu trong khi nghe người phụ nữ bên phải trò chuyện.

Câu query-p1-25-kis

Hai bạn học sinh mặc đồng phục áo trắng, quần xanh, quàng khăn đỏ đang làm MC trên một sân khấu tại trường học, phía sau là một bộ trống cơ màu đỏ và một cây đàn piano.

Question Answering (Q&A)

Câu query-p1-3-qa

Hình ảnh một con cá được đặt lên cân, sau đó có cảnh một con cá khác cùng loại bị một người cầm đuôi. Con số hiển thị cuối cùng trên cân là bao nhiêu?

Câu query-p1-9-qa

Đoạn phim ghi lại cảnh những chiếc xe ô tô lội nước, chiếc xe màu vàng, màu đỏ và màu đen lần lượt chuẩn bị đi qua cầu. Con số được ghi trên biển báo bên trái của cây cầu là bao nhiêu?

Câu query-p1-15-qa

Bản đồ phân bố động đất tại một vùng trên thế giới, với một bảng chú giải phía bên trái gồm các kí hiệu nhiều màu sắc tương ứng với các vị trí tâm chấn có cấp độ động đất khác nhau. Không tính bảng chú giải, có bao nhiêu vị trí ghi nhận động đất cấp độ 4?

Câu query-p1-17-qa

Đoạn clip mô tả hậu quả của hiện tượng sạt lở đất nghiêm trọng, đất đá tràn xuống gây tắc nghẽn hoàn toàn một đoạn đường đèo. Trong một cảnh quay cận, có thể thấy một cột mốc đường bộ với phần đỉnh màu đỏ chỉ còn lộ ra phần trên, phần lớn đã bị đất đá vùi lấp. Ở cảnh quay cuối, một người đi xe máy đang vật lộn để điều khiển phương tiện vượt qua khu vực bùn lầy, trên chiếc xe máy có treo một vật màu xanh lá. Tên của con đèo là gì?

Temporal Retrieval and Alignment of Key Events (TRAKE)

Câu query-p1-16-trake

Đoạn video bắt đầu bằng ảnh cận đầu một con lân trắng, mũi đỏ, bên cạnh lá cờ trắng viền đỏ.E1 Khoảnh khắc đầu tiên xuất hiện đầy đủ hai con rồng vàng đang xoay vòng.E2 Khoảnh khắc đầu tiên con lân hoàn tất cú xoay người trên các thanh trụ (thời điểm đâu tiên các chân của lân đặt trên trụ sau khi xoay).E3 Khoảnh khắc đầu tiên dùi chạm vào kẻng đồng múa lân.
