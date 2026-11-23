// App.jsx: React gọi 5 API của Django (không CSS, chỉ cần gọi API được là đủ)
import { useEffect, useState } from 'react';

const API = 'http://127.0.0.1:8000/api';

// ========== 1. GET /products/ : lấy danh sách sản phẩm ==========
function Products() {
  const [products, setProducts] = useState([]);

  // chạy 1 lần khi mở trang: gọi API rồi lưu kết quả vào state
  useEffect(() => {
    fetch(API + '/products/')
      .then((res) => res.json())
      .then((data) => setProducts(data.results));
  }, []);

  return (
    <div>
      <h2>Danh sách sản phẩm</h2>
      {products.map((p) => (
        <p key={p.id}>
          {p.title} - ${p.final_price} - người đăng: {p.author_name}
        </p>
      ))}
    </div>
  );
}

// ========== 2. GET /blogs/ : lấy danh sách blog ==========
function Blogs() {
  const [blogs, setBlogs] = useState([]);

  useEffect(() => {
    fetch(API + '/blogs/')
      .then((res) => res.json())
      .then((data) => setBlogs(data.results));
  }, []);

  return (
    <div>
      <h2>Danh sách blog</h2>
      {blogs.map((b) => (
        <div key={b.id}>
          <h3>{b.title}</h3>
          <p>{b.description}</p>
        </div>
      ))}
    </div>
  );
}

// ========== 3. POST /register/ : form đăng ký ==========
function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '' });
  const [message, setMessage] = useState('');

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault(); // không cho form tải lại trang
    const res = await fetch(API + '/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form), // gửi dữ liệu form sang Django
    });
    const data = await res.json();
    // thành công: server trả message, thất bại: trả error
    setMessage(res.ok ? data.message : data.error);
  }

  return (
    <div>
      <h2>Đăng ký</h2>
      <form onSubmit={handleSubmit}>
        <p><input name="username" placeholder="Tên đăng nhập" onChange={handleChange} /></p>
        <p><input name="email" placeholder="Email" onChange={handleChange} /></p>
        <p><input name="password" type="password" placeholder="Mật khẩu" onChange={handleChange} /></p>
        <p><input name="password2" type="password" placeholder="Nhập lại mật khẩu" onChange={handleChange} /></p>
        <button>Đăng ký</button>
      </form>
      <p>{message}</p>
    </div>
  );
}

// ========== 4. POST /login/ : form đăng nhập, nhận token ==========
function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await fetch(API + '/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem('token', data.token); // lưu token để các API cần đăng nhập dùng lại
      setMessage('Đăng nhập thành công, token: ' + data.token);
    } else {
      setMessage(data.error);
    }
  }

  return (
    <div>
      <h2>Đăng nhập</h2>
      <form onSubmit={handleSubmit}>
        <p><input name="username" placeholder="Tên đăng nhập" onChange={handleChange} /></p>
        <p><input name="password" type="password" placeholder="Mật khẩu" onChange={handleChange} /></p>
        <button>Đăng nhập</button>
      </form>
      <p>{message}</p>
    </div>
  );
}

// ========== 5. POST /my-products/create/ : thêm sản phẩm (cần token) ==========
function AddProduct() {
  const [title, setTitle] = useState('');
  const [price, setPrice] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    const token = localStorage.getItem('token'); // token lấy được lúc đăng nhập

    const data = new FormData(); // dùng FormData vì sau này có thể gửi kèm file hình
    data.append('title', title);
    data.append('price', price);

    const res = await fetch(API + '/my-products/create/', {
      method: 'POST',
      headers: { Authorization: 'Token ' + token }, // gửi token để Django biết ai đang thêm
      body: data,
    });
    const result = await res.json();
    setMessage(res.ok ? 'Đã thêm sản phẩm: ' + result.title : result.error || result.detail);
  }

  return (
    <div>
      <h2>Thêm sản phẩm (phải đăng nhập trước)</h2>
      <form onSubmit={handleSubmit}>
        <p><input placeholder="Tên sản phẩm" value={title} onChange={(e) => setTitle(e.target.value)} /></p>
        <p><input placeholder="Giá" value={price} onChange={(e) => setPrice(e.target.value)} /></p>
        <button>Thêm</button>
      </form>
      <p>{message}</p>
    </div>
  );
}

// ========== Trang chính: bấm nút để đổi trang ==========
export default function App() {
  const [page, setPage] = useState('products');

  return (
    <div>
      <h1>Shop - React gọi API Django</h1>
      <button onClick={() => setPage('products')}>Sản phẩm</button>
      <button onClick={() => setPage('blogs')}>Blog</button>
      <button onClick={() => setPage('register')}>Đăng ký</button>
      <button onClick={() => setPage('login')}>Đăng nhập</button>
      <button onClick={() => setPage('add')}>Thêm sản phẩm</button>
      <hr />
      {page === 'products' && <Products />}
      {page === 'blogs' && <Blogs />}
      {page === 'register' && <Register />}
      {page === 'login' && <Login />}
      {page === 'add' && <AddProduct />}
    </div>
  );
}
