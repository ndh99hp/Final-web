# Đồ án Web Bao Vic (Shop E-Shopper)

Web bán hàng chia 2 phần:
- **Backend:** Django + Django REST Framework (chỉ trả JSON), cơ sở dữ liệu MySQL (XAMPP).
- **Frontend:** ReactJS (Vite) trong thư mục `frontend-react`, gọi API của backend.

## 1. Yêu cầu
- Python + venv (Django 4.2, djangorestframework, django-cors-headers, pillow, django-ckeditor, mysqlclient)
- XAMPP (bật MySQL), tạo database trùng tên trong `core/settings.py`
- Node.js bản LTS (kiểm tra bằng `node -v`)

## 2. Chạy backend (terminal 1)
```
venv\Scripts\activate
python manage.py migrate
python manage.py createsuperuser     (chỉ lần đầu, để vào /admin/)
python manage.py runserver
```
- API: http://127.0.0.1:8000/api/
- Trang quản trị Django (tạo Blog, Category, Brand, Country): http://127.0.0.1:8000/admin/
- Danh sách API: xem file `API_DOCS.md`
- Chạy test: `python manage.py test api`

## 3. Chạy frontend (terminal 2)
```
cd frontend-react
npm install          (chỉ lần đầu)
npm run dev
```
Mở http://localhost:3000 (backend phải đang chạy).

## 4. Tài khoản
- Member: đăng ký ở http://localhost:3000/register
- Admin: đăng nhập ở http://localhost:3000/admin/login (tài khoản tạo bằng `createsuperuser`)

## 5. Phân quyền
- Member dùng được: giỏ hàng, thanh toán, lịch sử mua, sản phẩm của tôi, cập nhật tài khoản.
- Admin dùng được: quản lý user, sản phẩm, lịch sử mua hàng, tạo superuser.
- Đăng nhập bằng token (header `Authorization: Token <key>`).
