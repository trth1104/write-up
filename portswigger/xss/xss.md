# Lab 01: Reflected XSS into HTML context with nothing encoded
Chèn script vào trường search  
![alt text](images/xss/image.png)

# Lab 02: Stored XSS into HTML context with nothing encoded
Chọn một post bất kỳ, mỗi post sẽ có chức năng đăng tải comment.
Ta có thể chèn script vào nội dung comment để thực hiện stored xss
![alt text](images/xss/image-1.png)

# Lab 03: DOM XSS in document.write sink using source location.search
Đề yêu cầu tìm khai thác sink document.write với source location.search. Location.search là thuộc tính trả về kết quả truy vấn trong URL, ví dụ `abc.com?params=1` thì location.search trả về `?params=1`

Vì là một lỗi JS, mình xem thử các đoạn code script của trang xem sao. Mình tìm được một đoạn JS ở endpoint `/?search=` xử lý untrusted data `location.search`  
![alt text](images/xss/image-2.png)  

Đoạn script tạo một thẻ `img` mới, untrusted data trong `location.search` sẽ được thêm vào đường dẫn trong thuộc tính `src=`  
![alt text](images/xss/image-3.png)  

Vì script không thực hiện sàng lọc ký tự đặc biệt, nên mình sẽ thoát khỏi dấu nháy đổi của `src` và chèn thuộc tính `onload=alert(1)`.  
![alt text](images/xss/image-4.png)  

# Lab 04: DOM XSS in innerHTML sink using source location.search
Lab này chắc cũng tương tự với lab trên, sink sẽ nằm `?search=`, xài Dev tool tìm source `location.search` cho nhanh  
![alt text](images/xss/image-5.png)  

Untrusted data được thay đổi bằng `innterHTML.getElementById('searchMessage')`, search `id="searchMessage"`, thì nó chính thẻ có nội dung `search results...gì gì đó`.

Vì `innerHTML` không nhận thẻ `script` cũng như `svg`  
![alt text](images/xss/image-6.png) 

Vậy thì xài `<img onerror>`
![alt text](images/xss/image-7.png)  

# Lab 05: DOM XSS in document.write sink using source location.search inside a select element
Tìm được đoạn code JS với sink `location.search` trong thẻ `form`  
![alt text](images/xss/image-8.png)  

Đoạn code thực hiện hiển thị danh sách các cửa hàng bằng thẻ `<select>` và `<option>`, nếu có biến `store` thì danh sách hiển thị giá trị biến `store`, còn không thì duyệt các giá trị có trong danh sách `stores`.

Biến `store` là một untrusted data được truyền trực tiếp từ tham số `GET storeId`. Thay đổi tham số này thì danh sách `<select>` sẽ hiển thị option này.  
![alt text](images/xss/image-9.png)  

`GET storeId` được bao trong `<option selected>'+store+'</option>`, payload cần thoát được tag `<option>`, sau đó mới chèn script.
![alt text](images/xss/image-10.png)  

# Lab 06: Lab: DOM XSS in jQuery anchor href attribute sink using location.search source
Tìm được code JS với sink `location.search` trong endpoint `Submit Feedback`  
![alt text](images/xss/image-11.png)  

Đoạn code thực hiện thêm thuộc tính `href` vào thẻ có `id=backLink`. Giá trị thuộc tính `href` sẽ được lấy từ tham số `GET returnPath`.  

Ta biết script có thể được thực hiện thông qua các URI scheme, tham khảo: https://en.wikipedia.org/wiki/List_of_URI_schemes#Official_IANA-registered_schemes  

Đề yêu cầu `href` của thẻ có `id=backLink` phải trả về script, vậy để làm bài này, ta sẽ thay đổi giá trị của `GET returnPath` thành scheme `javascript:alert(1)`  
![alt text](images/xss/image-12.png)  

# Lab 07: DOM XSS in jQuery selector sink using a hashchange event
Tìm được đoạn JS với sink `location.hash` ở trang index.  
![alt text](images/xss/image-13.png)  

Giải thích sơ, `location.hash` trả về giá trị sau dấu `#` trên URL, ví dụ `https://abc.com/#xyz` thì trả về `#xyz`, `onhashchange` sẽ kích hoạt dựa trên sự thay đổi của phần tử này.  

Đoạn code dựa vào quy tắc trên để cuộn đến các nội dung của trang. Vị trí được cuộn tới lưu trong biến `post`  
```javascript
var post = $('section.blog-list h2:contains(' + decodeURIComponent(window.location.hash.slice(1)) + ')');
```
Biến `post` sẽ là các thẻ `<h2>` nằm trong thẻ `<selection class="blog-list">`, các thẻ `<h2>` phải chứa nội dung giống với `location.hash.slice(1)`, `slice(1)` nhằm lược đi dấu `#`, `#xyz` --> `xyz` 


```javascript
if (post) post.get(0).scrollIntoView();
```
`post.get(0)` nhằm chuyền từ đối tượng jQuery -> DOM bình thường, `scrollIntoView()` sẽ cuộn đến thẻ `<h2>` đó

PortSwigger cung cấp khá thiếu thông tin về sink `$()` của jQuery cũng như tại sao phải sử dụng payload là `<iframe...`. Đại khái là sink không chỉ cho phép truy cập DOM mà còn cho phép tạo thêm các thẻ mới. Dựa vào đó, ta có thể tạo và kích hoạt script với `<img onerror...` và `<iframe onerror...`, tham khảo https://web.stanford.edu/class/cs98si/slides/jquery.html#:~:text=We%20can%20create%20an%20element%20by%20passing,HTML%20element,%20with%20no%20naked%20text%20outside.  
Tới đây mình lại thắc mắc, nếu chèn thẻ `<img>` thì biến `post` trở thành
```javascript
var post = $('section.blog-list h2:contains('<img...onerror=alert(1)>')');
```
Thẻ `<img` bị bao trong hàm `contains()`, nhưng tại sao thẻ vẫn được render và thực thi. Đại khái, jQuery version 1.9 trở xuống xác định đối tượng trong đối tượng khá sơ sài. Trong bài này, do trong `$()` chứa dấu `<>` đã vô tình làm jQuery hiểu lầm đây là một HTML code, dẫn đến render đoạn HTML này.  
Tham khảo thêm:  
https://jquery.com/upgrade-guide/1.9/#jquery-htmlstring-versus-jquery-selectorstring  
https://nvd.nist.gov/vuln/detail/CVE-2012-6708

Bắt đầu khai thác, chèn `<img ... onerror=alert(1)>` test thử  
![alt text](images/xss/image-14.png)  

Tuy nhiên, nếu ta gửi `url/#<img...onerror=...>` như thế này, thì event hashchange sẽ không được trigger, dẫn đến thẻ `<img>` không được render. Do đó, ta sử dụng `<iframe>` truy cập url hiện tại và có event là `onload= "this.src= 'url-hiện-tại/#<img...>' "`. Đầu tiên, iframe truy cập url gốc, event onload sẽ được trigger, thay đổi hash từ `#` -> `#<img...>`, hashchange được trigger dẫn đến thực thi `<img>`
![alt text](images/xss/image-15.png)  

Bài này khá khoai do vận dụng jQuery nhưng PortSwigger lại cung cấp khá ít thông tin về payload cũng như cách jQuery hoạt động dẫn đến lỗi.

# Lab 08: DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded
Ái chà, bài này lại xài thư viện mới, đề bài có nói rằng AngularJS sẽ có hiệu lực với các thẻ có thuộc tính `ng-app`, các thẻ này có thể thực thi script trong cặp dấu `{{ script }}`.  

Ta tìm được endpoint search có thẻ `body` định nghĩa thuộc tính `ng-app`, nghĩa là toàn bộ các thẻ trong `body` đều chạy được `{{ script }}`, trong đó có trường trả về `search results for ...`   
![alt text](images/xss/image-16.png)


Tìm hiểu thêm, `{{ script }}` của Angular chỉ cho phép chạy các hàm nằm trong `$scope` được quy định trước, nên không thể chạy được các hàm không được định nghĩa trong scope `{{ alert(1) }}` cũng như là `{{ print() }}`.  

Ta có thể bypass bằng cách thay vì gọi trực tiếp, ta có thể sử dụng `constructor` để gọi gián tiếp hàm `alert()`, ví dụ `alert.constructor` sẽ trả về Function(), chuỗi a thì `a.constructor` trả về String(). Trong bài này, ta sử dụng `Function()`, vì nó cho phép ta khai báo động một `Function()`, gọi gián tiếp một hàm JS khác, bypass được sandbox của AngularJS.   
Tham khảo:  
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/Function#syntax    
https://portswigger.net/research/dom-based-angularjs-sandbox-escapes  

Vậy để khai thác, ta cần tìm một hàm có trong $scope của Angular, thêm phương thức constructor và lồng thêm hàm `alert(1)` vào   
![alt text](images/xss/image-17.png)  

# Lab 09: 