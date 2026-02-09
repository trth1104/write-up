# Exploit
- Đổi method
- Thử xóa giá trị csrf token
- Nếu token đổi, thì thử sử dụng token cũ
- Kiểm tra token của user này với user khác

# Defend
## Sử dụng token CSRF
**1. Tạo token**  
- Generate những token có **độ ngẫu nhiên** cao.  
- Token nên csrf nên được liên kết với session.  
- Kiểm tra kỹ từng case trước khi thực hiện yêu cầu.  

**2. Gửi token**  
- Nếu đặt bên trong HTML thì nên đặt ở đầu, hạn chế tin tặc chèn element vào trước.  
- Không nên đặt token trong cookie.
- Nên đặt trong header yêu cầu.

**3. Kiểm tra token**
- Nên tạo token theo session và lưu trên server
- Nên kiểm tra bất kể yêu cầu có method như thế nào đi chăng nữa.

## Sử dụng cookie thuộc tính SameSite
Nên chia ngữ cảnh cho cookie bằng cấu hình thuộc tính SameSite, hạn chế khả năng sử dụng cùng token tấn công nơi khác.  

## Kiểm tra header Referer
Thuộc tính SameSite là chưa đủ, vẫn còn khả năng bị tấn công cross-origin và same-site.  
Cần cô lập các endpoint nguy hiểm, hạn chế khả năng leo thang sang các nơi khác.