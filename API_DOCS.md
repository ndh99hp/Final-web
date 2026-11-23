# API của web Shop (E-Shopper)

Backend Django chỉ còn **model + view trả JSON** (Django REST Framework, Bài 22 và 23). Giao diện do ReactJS làm và gọi các API dưới đây.

- Địa chỉ gốc: `http://127.0.0.1:8000/api/`
- Mở `http://127.0.0.1:8000/api/products/` trên trình duyệt sẽ thấy giao diện thử API của DRF.
- Trang quản trị Django `http://127.0.0.1:8000/admin/` vẫn dùng để tạo Blog, Category, Brand, Country.

## 1. Cài đặt và chạy

```
pip install djangorestframework django-cors-headers
python manage.py migrate          # tạo bảng Token (authtoken) và bảng CartItem (giỏ hàng)
python manage.py runserver
python manage.py test api         # chạy test tự động (17 test)
```

Settings đã thêm: `rest_framework`, `rest_framework.authtoken`, `corsheaders`, `api`, `REST_FRAMEWORK`, `CORS_ALLOWED_ORIGINS`
(React chạy ở `localhost:3000` hoặc `localhost:5173`), `FRONTEND_URL` (dùng tạo link trong mail quên mật khẩu).

## 2. Cách gọi API

- Dữ liệu gửi lên: JSON (`Content-Type: application/json`) hoặc form-data (khi có upload hình).
- API cần đăng nhập: gửi header `Authorization: Token <key>` (key lấy từ `login/`, như Bài 23).
- Thành công: mã 200 / 201, dữ liệu JSON. Lỗi: mã 400 / 401 / 403 / 404 kèm `{"error": "..."}`.
- 401 = chưa đăng nhập / token sai. 403 = đăng nhập rồi nhưng không đủ quyền (admin gọi API member, member gọi API admin).
- Tiền là số (`12.5`). Hình là link đầy đủ (`http://127.0.0.1:8000/media/products/a.jpg`).
- Danh sách có phân trang trả về `{"count", "page", "total_pages", "results": [...]}`. Gửi `?page=2` để sang trang khác.

Ví dụ trong React:

```js
// đăng nhập
const res = await fetch("http://127.0.0.1:8000/api/login/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ username: "mem1", password: "123456" }),
});
const data = await res.json();          // { token: "...", user: {...} }
localStorage.setItem("token", data.token);

// gọi API cần token
const cart = await fetch("http://127.0.0.1:8000/api/cart/", {
  headers: { Authorization: "Token " + localStorage.getItem("token") },
}).then((r) => r.json());

// thêm sản phẩm (có hình): dùng FormData, KHÔNG tự đặt Content-Type
const form = new FormData();
form.append("title", "Áo thun"); form.append("price", "100");
form.append("images", file1);     form.append("images", file2);
fetch("http://127.0.0.1:8000/api/my-products/create/", {
  method: "POST", headers: { Authorization: "Token " + token }, body: form,
});
```

## 3. Danh sách API

Cột "Quyền": **Công khai** = ai cũng gọi được, **Member** = cần token của member, **Admin** = cần token của superuser, **Đã login** = token member hoặc admin.

### Tài khoản (sheet member/register, member/login, account/update, forget pass, auth-backend-frontend)

| Method | Đường dẫn | Quyền | Gửi lên | Trả về |
|---|---|---|---|---|
| GET | `countries/` | Công khai | | `[{id, name}]` cho ô chọn quốc gia |
| POST | `register/` | Công khai | `username, email, password, password2` (+ `first_name, last_name, id_country, phone, address, avatar`) | 201 `{message, token, user}`, gửi mail chào mừng |
| POST | `login/` | Công khai | `username, password` | `{token, user}`. Tài khoản admin bị từ chối (403) |
| POST | `logout/` | Đã login | | xóa token |
| GET | `account/` | Member | | thông tin user |
| PUT | `account/update/` | Member | các ô muốn đổi: `email, first_name, last_name, address, phone, id_country, password, avatar` | `{message, user}` |
| POST | `forgot-password/` | Công khai | `email` | gửi mail có link `FRONTEND_URL/reset-password/<uid>/<token>` |
| POST | `reset-password/` | Công khai | `uid, token, password, password2` | đổi mật khẩu (link dùng được 1 lần) |

### Sản phẩm (sheet home product, product-detail, search name, search-advanced, seacrh-price)

| Method | Đường dẫn | Quyền | Mô tả |
|---|---|---|---|
| GET | `filters/` | Công khai | Danh mục và hãng (kèm số sản phẩm), `price_ranges`, `sort_options`, `slider_max` (giá tối đa cho thanh kéo) |
| GET | `home/` | Công khai | 6 sản phẩm mới nhất |
| GET | `products/` | Công khai | Trang shop, 9 sản phẩm / trang. Lọc: `q` (tên), `category`, `brand`, `price=thấp,cao` (thanh kéo giá), `sort=price_asc / price_desc / name`, `page` |
| GET | `products/search/` | Công khai | Tìm kiếm nâng cao: `name`, `price` (`0-10`, `10-50`, `50-100`, `100-500`, `500-1000`, `1000-99999999`), `category`, `brand`, `status` (0 = New, 1 = Sale), `page` |
| GET | `products/<id>/` | Công khai | `{product, related}` (related = tối đa 6 sản phẩm cùng danh mục) |

Giá dùng để lọc / sắp xếp là giá hiện hành: sản phẩm Sale (status = 1) lấy giá sale, sản phẩm New lấy giá gốc (`final_price`).

### Sản phẩm của tôi (sheet my product, add product, edit product)

| Method | Đường dẫn | Quyền | Gửi lên |
|---|---|---|---|
| GET | `my-products/` | Member | `?q=` tìm theo tên, `?page=`, 10 sản phẩm / trang |
| POST | `my-products/create/` | Member | form-data: `title, price` (bắt buộc), `status` (0 / 1), `sale` (bắt buộc nếu status = 1, nhỏ hơn price), `category, brand, company, detail`, `images` (tối đa 3 file, mỗi file < 1MB, jpg / png / gif / webp) |
| PUT | `my-products/update/<id>/` | Member | như thêm, thêm `delete_images` (tên file hình muốn xóa, lấy từ đường dẫn hình). Hình cũ còn lại + hình mới <= 3 |
| DELETE | `my-products/delete/<id>/` | Member | xóa sản phẩm và file hình |

Chỉ sửa / xóa được sản phẩm của chính mình (sản phẩm của người khác trả 404).

### Giỏ hàng, thanh toán (sheet ADD TO CART, show-cart, checkout-sendmail)

Giỏ hàng lưu trong **database** (bảng `CartItem`) nên cần đăng nhập. Giá trong giỏ luôn là giá hiện tại của sản phẩm.

| Method | Đường dẫn | Quyền | Gửi lên | Trả về |
|---|---|---|---|---|
| GET | `cart/` | Member | | `{items:[{product_id, title, image, price, qty, total}], grand_total, cart_count}` |
| POST | `cart/add/` | Member | `product_id`, `qty` (1 đến 99, mặc định 1) | `{message, cart_count}` (số loại sản phẩm, hiện ở menu cart) |
| PUT | `cart/update/` | Member | `product_id`, `action` = `up` / `down` / `delete` | giỏ hàng mới (như `cart/`) |
| POST | `checkout/` | Member | `name, email, phone` (8 đến 15 chữ số) | 201 `{message, mail_sent, order}`. Lưu lịch sử, làm trống giỏ, gửi mail xác nhận |
| GET | `orders/` | Member | `?page=` | lịch sử mua hàng của mình |

### Blog (sheet Blog, Blog rate, Blog cmt)

| Method | Đường dẫn | Quyền | Gửi lên | Trả về |
|---|---|---|---|---|
| GET | `blogs/` | Công khai | `?page=` (3 bài / trang) | danh sách bài, mới nhất lên đầu |
| GET | `blogs/<slug>/` | Công khai (gửi token thì có `your_rate`) | | `{blog, comments (lồng nhau, mục replies), prev, next, rating}` |
| POST | `blogs/<slug>/rate/` | Đã login | `rate` (1 đến 5, mỗi người 1 lần) | `{your_rate, average, average_raw, count}` |
| POST | `blogs/<slug>/comment/` | Đã login | `cmt`, `parent_id` (nếu là trả lời) | `{message, comment}` |

### Admin (sheet Shop Admin, admin: list user-product). Tất cả cần token của superuser

| Method | Đường dẫn | Mô tả |
|---|---|---|
| POST | `admin/login/` | `username, password`, chỉ superuser mới nhận token |
| GET | `admin/users/` | Danh sách user: `?q=` (username / email), `?role=admin / member`, `?page=`. Mỗi user có `total_products` |
| PUT | `admin/users/update/<id>/` | Sửa member: `email, first_name, last_name, phone, address, id_country, is_active` (0 = khóa), `password` (bỏ trống = giữ) |
| DELETE | `admin/users/delete/<id>/` | Xóa member + sản phẩm + hình. Lịch sử mua hàng vẫn giữ |
| POST | `admin/users/register-superuser/` | Tạo superuser mới (`username, email, password, password2`) |
| GET | `admin/products/` | Tất cả sản phẩm: `?q=` (tên sản phẩm), `?member=` (tên member), `?page=` |
| PUT | `admin/products/update/<id>/` | Sửa bất kỳ sản phẩm (form-data như member sửa) |
| DELETE | `admin/products/delete/<id>/` | Xóa bất kỳ sản phẩm |
| GET | `admin/history/` | Lịch sử mua hàng: `results` (danh sách đơn, `?q=`, `?user=<id>`, `?page=`), `members` (thống kê theo member: số đơn, tổng tiền, ngày mua gần nhất), `summary` (tổng số đơn, tổng tiền) |

## 4. Phân quyền (sheet auth-backend-frontend)

- Admin = `is_superuser` hoặc `is_staff`. Member = cả hai đều False (đăng ký qua `register/` luôn là member).
- Member đăng nhập ở `login/`, admin đăng nhập ở `admin/login/` (đăng nhầm chỗ bị 403).
- API của member (`account`, `my-products`, `cart`, `checkout`, `orders`) từ chối token admin. API `admin/...` từ chối token member.

## 5. Các file API

```
api/serializers.py      đổi dữ liệu thành JSON (giống BlogSerializer Bài 22)
api/permissions.py      IsMember, IsSuperAdmin
api/helpers.py          kiểm tra dữ liệu, lọc sản phẩm, upload hình, phân trang
api/views_auth.py       đăng ký, login, logout, account, quên mật khẩu
api/views_product.py    sản phẩm + sản phẩm của tôi
api/views_cart.py       giỏ hàng, checkout, lịch sử
api/views_blog.py       blog, rate, comment
api/views_admin.py      admin
api/urls.py             đường dẫn
api/tests.py            test tự động
cart/models.py          thêm bảng CartItem (migration 0002_cartitem)
```
