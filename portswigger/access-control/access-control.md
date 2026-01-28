Chia làm Vertical (user-admin), Horizontal (user-user), và Context-dependent (user-guest)

# Lab 01: Unprotected admin functionality
Yêu cầu truy cập admin panel và xóa user carlos.  

Test thử với `/admin` ở đuôi.  
![alt text](images/access-control/image.png)  

Mình tiếp tục thử với `/robots.txt` xem config có chặn trang nào không.  
![alt text](images/access-control/image-1.png)  

Mình phát hiện trang web đang chặn bot truy cập trang `/administrator-panel`.  
Truy cập và chọn delete carlos là xong.  
![alt text](images/access-control/image-2.png)  

# Lab 02: Unprotected admin functionality with unpredictable URL
Yêu cầu truy cập admin panel và xóa user carlos.  

Hiện tại không thể truy cập `/robots.txt` và `/administrator-panel`.  
Mình có thử bruteforce đăng nhập nhưng không hiệu quả. Tuy nhiên, khi xem page source, mình phát hiện đoạn JS khả nghi.  
![alt text](images/access-control/image-3.png)  
```JS
var isAdmin = false;
if (isAdmin) {
   var topLinksTag = document.getElementsByClassName("top-links")[0];
   var adminPanelTag = document.createElement('a');
   adminPanelTag.setAttribute('href', '/admin-n5yrfu');
   adminPanelTag.innerText = 'Admin panel';
   topLinksTag.append(adminPanelTag);
   var pTag = document.createElement('p');
   pTag.innerText = '|';
   topLinksTag.appendChild(pTag);
}
```

Đoạn code kiểm tra xem người dùng hiện tại có phải là admin không, nếu phải thì tạo đường dẫn với thẻ `<a>` dẫn tới admin panel. Đoạn code vô tình để lộ đường dẫn tới admin panel là `/admin-n5yrfu`.  

Truy cập đường dẫn và xóa user.  
![alt text](images/access-control/image-4.png)   

# Lab 03: User role controlled by request parameter
Yêu cầu truy cập admin panel và xóa user carlos.  

Yêu cầu có đề cập đến `/admin`, mình thử truy cập xem sao.  
![alt text](images/access-control/image-5.png)  

Lab có cung cấp thông tin đăng nhập, thử đăng nhập và truy cập `/admin`, mình phát hiện dữ liệu khả nghi ở trường cookie.  
![alt text](images/access-control/image-6.png)  

Thử thay đổi thành True xem sao.  
![alt text](images/access-control/image-7.png)  

Dựa vào HTML của admin panel, mình tìm được endpoint để xóa user carlos là `/delete?username=carlos`, thêm đoạn này vào sau `GET /admin` của gói tin là xong.  
![alt text](images/access-control/image-8.png)  

# Lab 04: User role can be modified in user profile
Yêu cầu truy cập admin panel `/admin`, endpoint chỉ có thể truy cập được sử dụng `roleid=2`.  

Sử dụng thông tin đăng nhập được cung cấp, đăng nhập và truy cập thử admin panel.  
![alt text](images/access-control/image-9.png)  

Trong user panel, email có giá trị là `normal-user` khá đáng nghi.  

Khi thực hiện thay đổi email, trang web gửi yêu cầu, trong phản hồi có giá trị `roleId=1`.  
![alt text](images/access-control/image-10.png)  

Thử thêm biến `roleId=2` và gửi đi, phản hồi nhận lại đã thay đổi `roleId=2`.  
![alt text](images/access-control/image-11.png)  

Tiếp theo là truy cập `/admin` và xóa user được yêu cầu.  
![alt text](images/access-control/image-12.png)  

# Lab 05: User ID controlled by request parameter 
Lab có lỗi quản lý truy cập theo chiều ngang, ở trang tài khoản người dùng, yêu cầu tìm API key của user carlos.  

Sau khi đăng nhập, truy cập trang user account sẽ hiện ra API của người dùng hiện tại.  
![alt text](images/access-control/image-13.png)  

Thử thay đổi email, ta có được 2 untrusted data là `email` và `csrf`.  
![alt text](images/access-control/image-14.png)  

Nếu để ý kỹ, trên URL có thêm untrusted data là `id=wiener`, vậy sẽ ra sao nếu mình đổi thành carlos.  
![alt text](images/access-control/image-15.png)  

Kết quả là mình có được key của carlos.  
![alt text](images/access-control/image-16.png)  

# Lab 06: User ID controlled by request parameter, with unpredictable user IDs 
Lab có lỗi quản lý truy cập theo chiều ngang ở trang tài khoản người dùng, quản lý user bằng userId, yêu cầu tìm API key của user carlos.  

Lab này khác với lab trước, userID đã bị làm nhiễu, không thể đoán được.  
![alt text](images/access-control/image-18.png)  

Thử quăng ID vào Burp Decoder xem liệu id có được encode từ gì không, nhưng kết quả không thành công.  
![alt text](images/access-control/image-19.png)  

Duyệt tiếp các chức năng, khi mình chọn một bài đăng bất kỳ, mình phát hiện tên tác giả bài đăng là đường dẫn có chứa userId.  
![alt text](images/access-control/image-20.png)  

Khi mình click vào tên tác giả, trỏ đến trang các bài post của user, tuy nhiên, tham số GET có chứa userID.   
![alt text](images/access-control/image-21.png)  

Nắm được điều này, mình duyệt các bài post tìm coi có user `carlos` không, kết quả mình tìm được bài đăng.   
![alt text](images/access-control/image-22.png)  

Nhấp vào `carlos`, ta lấy được userId.  
![alt text](images/access-control/image-23.png)  

Ta biết được endpoint `/my-account` bị lỗi IDOR. Truy cập endpoint `/my-account`, thay id hiện tại bằng id của carlos, mình lấy được key của user.  
![alt text](images/access-control/image-24.png)

# Lab 07: User ID controlled by request parameter with data leakage in redirect 
Lab bị lỗi access control, làm lộ thông tin nhạy cảm trong gói tin trả về khi thực hiện chuyển hướng. Yêu cầu lấy API key của carlos.  

Mình nhận ra một hành vi đáng ngờ khi thay đổi id ở trang user account.  
Nếu một user không tồn tại, thì phản hồi không có body. Ngược lại, sẽ có body HTML.  
Thử với `test`
![alt text](images/access-control/image-25.png)  
Thử với `carlos`  
![alt text](images/access-control/image-26.png)  

Đọc thử nội dung gói tin phản hồi khi thử với `carlos`, mình phát hiện server đã vô tình trả về panel của carlos, nhưng trên trình duyệt sẽ chuyển hướng, khiến ta vô tình bỏ quả gói tin. Panel này để lộ API key của `carlos`.  
![alt text](images/access-control/image-27.png)   

# Lab 08: User ID controlled by request parameter with password disclosure
Trang user account của bài lab chứa password của người dùng hiện tại. Yêu cầu truy cập và lấy password user carlos.  

Đăng nhập, chúng ta sẽ có trang account như sau.  
![alt text](images/access-control/image-28.png)  

Mặc dù password đã bị mask, nhưng giá trị lại được lưu trong HTMl, hoàn toàn có thể truy cập bằng devtool.  
![alt text](images/access-control/image-29.png)  

Đề bài cho ta biết rằng trên hệ thống hiện tại đang có user carlos, thử thay đổi biến `GET userid=carlos`, xem ta có thể truy cập được thông tin người dùng khác không, kết quả thành công.  
![alt text](images/access-control/image-30.png)  

Đề yêu cầu truy cập admin panel và xóa user carlos. Mình có thể thay đổi `userid` truy cập trang người dùng của admin. Từ đây, mình có thể lấy được password lưu ở trong HTMl. Mình sử dụng password lấy được, truy cập admin panel và xóa user carlos.  

Thay đổi `userId=administrator`, truy cập được trang account, từ đó lấy được passowrd admin là `p49w9iw31nwzvb059k83`.  
![alt text](images/access-control/image-31.png)  

Logout user hiện tại và đăng nhập user admin với password lấy được, đăng nhập thành công, mình có thêm chức năng admin panel, truy cập và xóa user.  
![alt text](images/access-control/image-32.png)  

# Lab 09: Insecure direct object references 
Lab lưu chat logs trên server, có thể truy cập bằng đường dẫn tĩnh. Yêu cầu lấy password và đăng nhập user carlos.  

Lỗi nằm ở việc lưu chat log, nên mình thử chức năng của `live chat` trước.  
![alt text](images/access-control/image-33.png)  

Trang `live chat` sẽ có 2 chức năng chính là gửi tin nhắn Send và View Transcript. View Transcript sẽ tải về file text nội dung đoạn chat hiện tại.  
![alt text](images/access-control/image-34.png)  

Kiểm tra gói tin, không phát hiện điều gì bất thường.  
![alt text](images/access-control/image-35.png)  

Thử kiểm tra các bài post xem có đoạn chat nào không, kết quả là không.  
![alt text](images/access-control/image-36.png)  

Thử view source tìm đường dẫn tĩnh đến nơi lưu các đoạn chat, có vẻ chức năng View Transcript được quản lý bởi JS trong file này.   
![alt text](images/access-control/image-37.png)  
![alt text](images/access-control/image-38.png)   

Đoạn code cũng không giúp gì nhiều, thử với file js còn lại `chat.js`.  
![alt text](images/access-control/image-39.png)  

Cả hai đoạn code cũng không giúp gì nhiều, tới đây mình chợt nhận ra, các transcript mình tải về nãy giờ bắt đầu từ id 2.  
![alt text](images/access-control/image-40.png)  

Thử thay đổi tên file thành `1.txt`.  
![alt text](images/access-control/image-41.png)  

Kết quả là mình lấy được đoạn chat khả nghi, vô tình lộ password `9up9pofmbxjbhxgndbap`.   
![alt text](images/access-control/image-42.png)   

# Lab 10: URL-based access control can be circumvented
