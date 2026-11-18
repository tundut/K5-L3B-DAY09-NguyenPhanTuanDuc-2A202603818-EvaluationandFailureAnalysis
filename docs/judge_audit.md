# Judge audit

Nhãn FAIL là lớp dương. FLOORS: κ ≥ 0.6, P ≥ 0.8, R ≥ 0.7; κ không xác định phải FAIL. Chạy hai lệnh `lab9.judge --csv data/eval/judge_<tone|helpful>_public.csv --audit 5` từ `src/`; output nguyên bản ở [validation.md](validation.md).

| Tiêu chí | n | κ | Precision | Recall | Ma trận TP/FP/FN/TN | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.8 | {'tp': 24, 'fp': 4, 'fn': 6, 'tn': 66} | Dùng cho tone trong miền replay |
| helpful | 100 | 0.375 | 1.0 | 0.3 | {'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70} | Loại khỏi gate |

## Năm bất đồng tone

Đây là phân tích rubric dựa trên nhãn human có sẵn, không phải nhãn người mới hay một vòng audit độc lập. Các hành động dưới đây là đề xuất sửa rubric; CSV replay giữ nguyên.

| Case | Judge | Human | Đánh giá và hành động |
|---|---|---|---|
| H-008 | PASS | FAIL | Nhãn human phù hợp rubric trang trọng: “anh … nha”, “check” dùng giọng thân mật. Thêm ví dụ FAIL cho xưng hô/khẩu ngữ. |
| H-017 | PASS | FAIL | Nhãn human phù hợp: trộn “Dạ” với “bạn ơi … nha”. Không cho từ lịch sự đầu câu che giọng thân mật cả câu. |
| H-029 | PASS | FAIL | Nhãn human phù hợp: “không cần nhắn thêm” tạo giọng gạt bỏ. Bổ sung tiêu chí tôn trọng quyền hỏi tiếp. |
| H-042 | FAIL | PASS | Nhãn human phù hợp: câu lịch sự, có thời gian tiền về; không bắt buộc khuôn mẫu dài hoặc đủ tên thương hiệu. |
| H-051 | FAIL | PASS | Theo nhãn human, từ “refund” không tự động làm sai tone. Tách quy tắc thuật ngữ khỏi tiêu chí thái độ. |

Rogan–Gladen: tone observed 0.28 → corrected 0.3; helpful 0.09 → 0.3. Không dùng tỉ lệ đã hiệu chỉnh để thay đổi nhãn từng trial.

Helpful có precision cao nhưng bỏ sót 21/30 lỗi (recall=0.3); κ=0.375 không đạt sàn. Câu lịch sự có thể sai số tiền hoặc không giải quyết yêu cầu, nên judge này không được làm gate. Cần rubric helpful kiểm đúng yêu cầu, thông tin đủ và kết quả đúng, sau đó đánh giá trên tập held-out mới. Tiền và approval luôn chấm bằng code. Tone qua calibration nhưng chưa được tích hợp làm blocking metric vì eval hiện không có nhãn tone độc lập cho từng trial.
