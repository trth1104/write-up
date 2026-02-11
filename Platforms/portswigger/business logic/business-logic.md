# Lab 01: Excessive trust in client-side controls
Lab này không validate unstrusted data, mua sản phẩm có tên là `Lightweight l33t leather jacket` để hoàn thành bài lab.  

Trong quá trình thanh toán sản phẩm, mình vấp phải vấn đề thiếu tiền để thanh toán.  
![alt text](images/business-logic/image.png)  

Nếu không đủ tiền để thanh toán, trình duyệt sẽ gửi yêu cầu có `INSUFFICIENT_FUNDS`.  
![alt text](images/business-logic/image-1.png)  

Mình thử mua món hàng khác xem sao, gói tin sẽ như sau.  
![alt text](images/business-logic/image-2.png)  

Kiểm tra lại, khi mình nhấn `Add to cart`, trình duyệt gửi yêu cầu như sau.  
![alt text](images/business-logic/image-3.png)  

Phân tích gói tin, mình nhận thấy có thể thay đổi các biến nhạy cảm như `price` và `redir`. Như đã biết thông qua các gói tin trên, có thể truyền `CART` vào `redir` chuyển hướng đến trang giỏ hàng.  
Thử đổi `redir=CART` và `price=1`, và `Open request in browser` kết quả thành công thay đổi giá món hàng.   
![alt text](images/business-logic/image-4.png)  
![alt text](images/business-logic/image-5.png)  

# Lab 02: High-level logic vulnerability
Lab này không validate unstrusted data, mua sản phẩm có tên là `Lightweight l33t leather jacket` để hoàn thành bài lab.  

Thử thêm sản phẩm vào giỏ hàng, trình duyệt gửi gói tin như sau.  
![alt text](images/business-logic/image-6.png)  

Lần này thì gói tin không còn biến `price` như lab trước. Tuy nhiên, biến `quantity` có thể thay đổi được.  

Có thể trang web tính tổng tiền bằng `total=price*quantity`. Thử thay đổi `quantity` thành số âm và `redir=CART`. Kết quả giá tiền thành âm.   
![alt text](images/business-logic/image-7.png)  

Bị báo lỗi tổng tiền không thể có giá trị âm.  
![alt text](images/business-logic/image-8.png)  

Vậy nếu mình nhập các số thập phân <1 (0.1, 0.5) thì sao, kết quả không thành công.    
![alt text](images/business-logic/image-9.png)  

Tổng tiền còn có thể tính bằng `total=product1+product2`. Vậy nếu mình thêm 1 sản phẩm khác, và cho giá tiền sản phẩm đó là âm thì sao.  
Thêm sản phẩm `id=2`, xem thử có giá bao nhiêu.  
![alt text](images/business-logic/image-10.png)  

Ta có `1337/1.63 = 820.25`, vậy mình đổi gói tin thành như sau.  
![alt text](images/business-logic/image-11.png)  
![alt text](images/business-logic/image-12.png)  


# Lab 03: Inconsistent security controls
Lab có lỗi logic cho phép người dùng bình thường truy cập các tính năng của admin. Yêu cầu sử dụng admin panel để xóa user `carlos`.  

Trong endpoint `/register`, có dòng thông báo yêu cầu domain mail là `@dontwannacry.com`.  
![alt text](images/business-logic/image-13.png)  

Thử đăng ký với email được lab cung cấp trong `Email Client`.  
![alt text](images/business-logic/image-14.png)  

Sau khi đăng ký, tại mail client sẽ có mail đăng ký tài khoản, nhấp vào để bắt đầu sử dụng tài khoản.  
![alt text](images/business-logic/image-15.png)  

Sau khi đăng nhập, mình có panel cho phép thay đổi email.  
![alt text](images/business-logic/image-16.png)  

Dựa vào thông báo ở `/register`, thử thay đổi email domain thành `@dontwannacry.com`.  

Sau khi đổi, ta sẽ có `Admin panel`. Truy cập và mình có thể xóa user `carlos`.  
![alt text](images/business-logic/image-17.png)  
![alt text](images/business-logic/image-18.png)  

# Lab 04: Flawed enforcement of business rules
Lab có lỗi trong workflow mua hàng, mua sản phẩm có tên là `Lightweight l33t leather jacket` để hoàn thành bài lab.  

Mình có thông tin về Coupon code mới.  
![alt text](images/business-logic/image-19.png)  

Mình phát hiện được endpoint mới, nhập email đăng ký nhận thông báo. Khi mình nhập email thì nhận được coupon mới.  
![alt text](images/business-logic/image-20.png)  

Coupon này giảm 30% giá trị sản phẩm, đồng thời, trên cửa hàng đang có item có giá 5.40$, nếu mình áp dụng cả 2 coupon, có khả năng tổng tiền < 0.  
![alt text](images/business-logic/image-21.png)  

Vậy mình có thể gửi nhiều lần 1 coupon không. Mình phát hiện 1 điều thú vị, khi gửi cùng coupon 2 lần sẽ bị lỗi `already applied`, tuy nhiên nếu gửi đan xen 2 coupon thì mình có thể sử dụng coupon nhiều lần.    
![alt text](images/business-logic/image-22.png)  

Sau vài lần thì item sẽ miễn phí.  
![alt text](images/business-logic/image-23.png)  

# Lab 04: Low-level logic flaw
Lab này không validate unstrusted data, mua sản phẩm có tên là `Lightweight l33t leather jacket` để hoàn thành bài lab.  

Một số hint trên trang lý thuyết
![alt text](images/business-logic/image-24.png)  

Gói tin thêm giỏ hàng như sau.  
![alt text](images/business-logic/image-25.png)  

Đầu tiên, mình thử tăng số lượng sản phẩm liên tục xem, server có cấu hình giới hạn không.  

Tuy nhiên, server chỉ cho phép gửi yêu cầu thêm số lượng sản phẩm < 100 mỗi lần.  

Sử dụng intruder nhằm gửi liên tục các gói tin này.  

Sau một hồi spam gói tin, tải lại trang web, tổng tiền bỗng < 0, mình đoán là biến lưu giá sản phẩm đã bị buffer overflow.  
![alt text](images/business-logic/image-26.png)  

Nếu dừng tấn công và tải lại, thì số lượng sản phẩm giảm xuống và tổng tiền quay về dương.  
![alt text](images/business-logic/image-27.png)  

Tổng tiền lúc này đang đan xen vòng lặp giá trị âm và dương

Mình nhận ra rằng sau khi lặp 200 lần, tổng tiền sẽ ra âm, mỗi lần tăng, tổng tiền sẽ cộng thêm 1337, tiến về giá trị 0. 

Hiện tại mình đang dừng tại ` 27423` và tổng tiền là ` 	-$6285121.96`.  
![alt text](images/business-logic/image-29.png)  

Nếu tăng số lượng thì tổng tiền +1337, theo mình tính, thì tốn khoảng 47 lần lặp gói tin để giá trị về gần 0.  

Mình tính số lần phải lặp tiếp bằng `tổng tiền / 1337 / 99`.  

Thêm sản phẩm nữa và điều chỉnh số lượng để tổng tiền trong khoảng 0-100.  

Sau một hồi thì mình cũng chỉnh được giá trị về số đẹp.  
![alt text](images/business-logic/image-30.png)  

Chọn món hàng có giá lớn nhất và điều chỉnh để tổng tiền 0-100.  
![alt text](images/business-logic/image-31.png)  