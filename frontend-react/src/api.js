// api.js: hàm gọi API của Django (fetch). Tự gắn token nếu đã đăng nhập
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export function getToken() {
  return localStorage.getItem('token');
}

// path: ví dụ '/products/'
// options.method: GET, POST, PUT, DELETE
// options.params: object tham số trên URL (ô trống sẽ bỏ qua), ví dụ { q: 'ao', page: 2 }
// options.body: object (gửi JSON) hoặc FormData (gửi form có file)
export async function api(path, options = {}) {
  const { method = 'GET', params, body } = options;

  let url = API_URL + path;
  if (params) {
    const query = new URLSearchParams();
    Object.keys(params).forEach((key) => {
      if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
        query.append(key, params[key]);
      }
    });
    const text = query.toString();
    if (text) url += '?' + text;
  }

  const headers = {};
  const token = getToken();
  if (token) headers['Authorization'] = 'Token ' + token;

  let sendBody;
  if (body instanceof FormData) {
    sendBody = body; // trình duyệt tự đặt Content-Type cho form-data
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    sendBody = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(url, { method, headers, body: sendBody });
  } catch (e) {
    throw new Error('Không kết nối được tới máy chủ. Hãy kiểm tra Django đã chạy chưa (python manage.py runserver)');
  }

  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }

  if (!res.ok) {
    // token sai / hết hạn: xóa thông tin đăng nhập để giao diện quay về trạng thái chưa đăng nhập
    if (res.status === 401 && token) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.dispatchEvent(new Event('auth-expired'));
    }
    const message = (data && (data.error || data.detail)) || 'Có lỗi xảy ra (mã ' + res.status + ')';
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }
  return data;
}

// Đổi link hình (http://127.0.0.1:8000/media/products/a.jpg) thành tên file lưu trong media (products/a.jpg)
// Dùng khi muốn xóa hình: API cần tên file
export function mediaName(url) {
  try {
    return decodeURIComponent(new URL(url).pathname.replace(/^\/media\//, ''));
  } catch (e) {
    return url;
  }
}
