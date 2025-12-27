# Mục tiêu
- Lấy các bí mật sau đây để chứng minh khai thác thành công
    - ✅ Flag 1: Khi thực hiện mua thành công Flag
    - ✅ Flag 2: Trong source code
    - ✅ Flag 3: Order details của user `conmeo`
    - ✅ Flag 4: Trong database
    - ✅ Flag 5: RCE thành công (Flag nằm ở thư mục `/` trên server)

# Untrusted data
## Login `/api/v2/auth/login`
- username
- password  

Sau khi đăng nhập, server trả về nội dung gói tin
```
"message":"Login successful",
"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcm5hbWUiOiJ2dWFkb3NhdCIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNzY0Mzg2ODU0LCJleHAiOjE3NjQ5OTE2NTR9._ts3w7dEDGFZ_PaTuSqv5YDQj2WFSyR0-3V_Yw4drCI",
"user":{
    "id":3,"username":"vuadosat",
    "role":"user",
    "balance":10,
    "email":"a@gmail.com",
    "image":"http://cdn.musoe.cyberjutsu-lab.tech/files/images/avatar/user.png"
    }
```
## Forgot password
- email
## Register `/api/v2/auth/register`
- username
- email
- password
## Order 
Tạo order `/api/v2/orders/create`
- id
- name
- image
- price
- description

Trả về:
```
{"message":"Order created","balance":0}
```

Lấy danh sách orders `/api/v2/orders`  
Lấy order detail `/api/v2/orders/{order_id}/detail`
## Send Ticket `/api/v2/tickets/create`
- subject
- description

## Load image `/api/v2/image/resize?image={url}&size={size}`
- image (url)
- size

# Khai thác
## Bị lỗi người dùng có thể tùy chỉnh số dư
Trong gói tin thực hiện chức năng đặt hàng ở `/api/v2/orders/create`, mình tìm thấy param `price` ở request và param `balance` ở response. Mình đoán là chương trình thực hiện phép toán `balance=current_balance - price` cho giao dịch.  
![alt text](images/musoe/image.png)  

Vậy sẽ ra sao nếu mình thay đổi `price` thành 0? Sau khi thay đổi, kết quả là mình có thể mua toàn bộ mặt hàng với giá 0 đồng.  
![alt text](images/musoe/image-2.png)  

Dựa vào dữ kiện trên, mình thực hiện giao dịch với mặt hàng flag, kiếm được flag đầu tiên  
![alt text](images/musoe/image-3.png)  

**FLAG** CBJS{ab413281962b76090c0db9051c05d2f2}

## Lộ đường dẫn .git
![alt text](images/musoe/image-4.png)  

Sử dụng git-dumper để pull, tuy nhiên không có kết quả.

## Chức năng xử lý đường dẫn chức năng Load Image cho phép xử lý đường dẫn bên ngoài dẫn đến truy cập file `.env`
![alt text](images/musoe/image-5.png)  

Chức năng này cho phép ta đọc nội dung của file, vậy sẽ ra sao nếu ta thay đổi đường dẫn thành một tệp tin có trên server  
Thử đọc đường dẫn `file:///etc/passwd` thành công. Lưu ý phải bỏ trống tham số `size`  
![alt text](images/musoe/image-6.png)  

Thử với những trường hợp khác thì server báo lỗi, dựa vào message, đoán được trang web đang sử dụng nodejs  
![alt text](images/musoe/image-7.png)  

Tìm được 2 đường dẫn:
- /usr/app/src/controllers/imageController.js
- /usr/app/node_modules/get-uri/dist/file.js

Đối với dự án Nodejs, file `.env` là một file nhạy cảm, lưu thông tin cấu hình, mật khẩu hoặc username. Dưới đây là cấu trúc file phổ biến của một dự án Nodejs.    
![alt text](images/musoe/image-8.png)  

Dựa vào cấu trúc trên và 2 đường dẫn file thu thập được, ta có thể đoán file `.env` có thể nằm ở đường dẫn `/usr/app/src/.env` và `/usr/app/.env`. Thử thành công với đường dẫn `/usr/app/src/.env`, có được flag thứ 2.
![alt text](images/musoe/image-9.png)  

**FLAG** CBJS{4d2c7fee2a055bd1e319826229f019db}

Đồng thời, ta thu được thêm 1 số thông tin như sau:
![alt text](images/musoe/image-27.png)

## Lộ token Github dẫn đến truy cập được file source code
Dựa vào thông tin trong file `.env`, ta có được thông tin repo github dự án


## Lộ thông tin đăng nhập MySQL

## Lộ secret token JWT+src code cho phép xây dựng token truy cập trái phép tài khoản người khác

## Lỗi SQLi trong Reset Password
Tại endpoint `POST /api/v2/auth/forgot-password`, khi ta thử nhập email với ký tự đặc biệt `'` và `"`, server báo lỗi `SQL syntax`  
![alt text](images/musoe/image-10.png)  

Trong thông báo lỗi, server có trả về thêm hàm và vị trí file bị lỗi. Dựa vào thông tin trên, phát hiện được file khả nghi `fogortPassword (/usr/app/src/controllers/authController.js:93:29)` và `User.findByEmail (/usr/app/src/models/user.js:25:29)`  

Kết hợp với lỗi đọc file trong api `LoadImage`, ta đọc nội dung 2 file này.  
Đối với file `authController.js` không phát hiện được điều gì. Tuy nhiên trong file `user.js`, tìm được nhiều hàm thực hiện truy vấn. Một trong số đó, có hàm findByEmail(email) thực hiện truy vấn SQL nguy hiểm.  
```javascript
 static async findByEmail(email) {
    const [rows] = await db.execute(`SELECT * FROM users WHERE email = '${email}'`);
    return rows[0] || null;
  }
```

Truy vấn `SELECT * FROM users WHERE email = '${email}'`  
Có được câu truy vấn trong chương trình, tuy nhiên hiện tại, chúng ta chưa tìm được endpoint trả kết quả truy vấn. Nên ta có thể phải tấn công `SQLi` bằng kỹ thuật `Error Based`  

Thử lấy `version()` của db server với payload `a@gmail.com' AND EXTRACTVALUE(1,CONCAT(' ','|',(SELECT version()),'|'))--` --> version = 8.0.42  
![alt text](images/musoe/image-11.png)  

Tìm tên các tables với `a@gmail.com' AND EXTRACTVALUE(1,CONCAT(' ','|',(SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=DATABASE()),'|'))--` --> tables: `flags,orders,products,tickets`  
![alt text](images/musoe/image-12.png)  

Lấy tên cột của bảng `flags` với `a@gmail.com' AND EXTRACTVALUE(1,CONCAT(' ','|',(SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='flags'),'|'))--` --> tìm được `flag,id`  
![alt text](images/musoe/image-13.png)  

Đọc flag với `a@gmail.com' AND EXTRACTVALUE(1,CONCAT(' ','|',(SELECT flag FROM flags),'|'))--`. Tuy nhiên chỉ lấy được 1 phần của flag (32 ký tự) `CBJS{76906e5c78c1f04ac35a143e4d`. Thêm hàm `Substring()` để lấy toàn bộ.  
![alt text](images/musoe/image-14.png)  


Payload với hàm substring() `a@gmail.com' AND EXTRACTVALUE(null,CONCAT('~',SUBSTRING((SELECT flag FROM flags LIMIT 1),10),'~'))--`  --> `6e5c78c1f04ac35a143e4de23a77}`  
![alt text](images/musoe/image-15.png)  

**FLAG** CBJS{76906e5c78c1f04ac35a143e4de23a77}  

Thử sử dụng SQLi để lấy password của `conmeo`--> `$2a$10$YSUjXFfVUTUdzJUyaBlInOb8` có vẻ password đã được hash bằng bcrypt, crack khá lâu nên bỏ qua.

## Tìm được sign token trong source code
Khi đăng nhập thành công, mỗi người dùng sẽ được cấp một token cho phiên.  
![alt text](images/musoe/image-17.png)  
Với cấu trúc của token như thế này, ta đoán được trang web sử dụng JWT token để quản lý phiên.  

Dựa vào thông tin trên, ta tập trung tìm các hàm có liên quan đến token này. 
Cấu trúc token lưu ở biến `token` trong file `authController`, dựa vào thông tin này + secret key trong file `.env`, ta có thể xây dựng token truy cập vào người dùng khác trên trang web
```js
const token = JWTHelpers.sign({
      id: user.id,
      username: user.username,
      role: user.role
    });
```

Ta thêm những dữ kiện trên vào công cụ JWT Token encoder xây dựng token. Sau đó, sử dụng devtool thay đổi `token, user` trong mục local storage.
![alt text](images/musoe/image-18.png)  

Sau khi thay đổi, ta nhấn tải lại, load trang orders lấy flag thứ 2 trong order list của con mèo.  
![alt text](images/musoe/image-19.png)  

**FLAG** CBJS{da825564095d09d173359085b3fe58c0}  

## Leo thang đặc quyền lên admin với thông qua token
Ta biết được rằng có thể truy cập tài khoản người dùng khác thông qua token. Vậy sẽ ra sao nếu ta sử dụng cách này để leo thang lên user admin của trang web.  
User của ta `vuadosat có id=3` và `conmeo có id=1` vậy rất có thể `admin có id=1`.  

Khai thác tương tự như khai thác user `conmeo`, đầu tiên, ta xây dựng token với thông tin của `admin`  
![alt text](images/musoe/image-20.png)  

Sau đó, ta chỉnh sửa tại `token, user` trong local storage thông qua dev tool.  
![alt text](images/musoe/image-21.png)  

Qua đó, ta tìm được thêm surface mới `Admin Panel`  
![alt text](images/musoe/image-22.png)  

Trang `Admin Panel` có 2 chức năng
- Đọc tickets
- Quản lý plugins trang web

Mình đã thử gửi tickets kiểm tra xem liệu chức năng tickets có bị XSS không, tuy nhiên tickets lại không lưu trong danh sách  
![alt text](images/musoe/image-23.png)  

Chức năng plugins cho phép admin thêm, tải và thực thi plugin có trong danh sách. Kiểm tra trong source code, các hàm phụ trách chức năng này không có bất kỳ phương thức kiểm tra nào cả.  

Khi ta nhấn tải về sẽ download một plugin template, cho phép ta viết một plugin hoàn toàn mới. Vậy sẽ ra sao nếu ta viết một shell js và thực thi command?  
![alt text](images/musoe/image-26.png)  

Một lưu ý là khi plugin được thực thi, sẽ không có endpoint trả về mà ta chỉ nhận được thông báo là plugin đã được thực thi. Từ đó, ý tưởng của ta sẽ là thực thi shell code và gửi dữ liệu về webhook.  

Khó khăn tiếp theo là khi nhấn vào upload plugin, ta nhận được thông báo chức năng hiện tại đang bảo trì. Kiểm tra trong source code, ta phát hiện với api `/api/v2/plugins`, mục upload plugin đã được anh dev comment lại. Tuy nhiên, chức năng này lại có xuất hiện ở api `/api/v1/plugins`.  

Dựa trên nhũng dữ kiện trong source code, để upload file, ta đổi đường dẫn từ `v2` thành `v1`, thêm JWT Token của admin, đổi request method, đổi encoding sang multipart kèm với file shell của mình.   
![alt text](images/musoe/image-24.png)  

Ta tiếp tục upload với lệnh `ls /` lấy được tên file flag, sau đó là `cat` và đọc flag.  
![alt text](images/musoe/image-25.png)  

**FLAG** CBJS{632f7879b5bea6fa83696b81e44e3943}
