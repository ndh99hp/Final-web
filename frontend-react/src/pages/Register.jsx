// Register.jsx: đăng ký member (có chọn quốc gia, upload avatar)
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../auth';
import Notice from '../components/Notice';

export default function Register() {
  const { saveLogin } = useAuth();
  const navigate = useNavigate();
  const [countries, setCountries] = useState([]);
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '', first_name: '', last_name: '', phone: '', address: '', id_country: '' });
  const [avatar, setAvatar] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/countries/').then(setCountries).catch(() => {});
  }, []);

  function setField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    const data = new FormData();
    Object.keys(form).forEach((k) => data.append(k, form[k]));
    if (avatar) data.append('avatar', avatar);
    try {
      const d = await api('/register/', { method: 'POST', body: data });
      saveLogin(d.token, d.user); // đăng ký xong tự đăng nhập luôn
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section id="form">
      <div className="container">
        <div className="row">
          <div className="col-sm-6 col-sm-offset-3">
            <div className="signup-form">
              <h2>Đăng ký thành viên</h2>
              <Notice>{error}</Notice>
              <form onSubmit={handleSubmit}>
                <input type="text" name="username" placeholder="Tên đăng nhập *" value={form.username} onChange={setField} required />
                <input type="email" name="email" placeholder="Email *" value={form.email} onChange={setField} required />
                <input type="password" name="password" placeholder="Mật khẩu (từ 6 ký tự) *" value={form.password} onChange={setField} required />
                <input type="password" name="password2" placeholder="Nhập lại mật khẩu *" value={form.password2} onChange={setField} required />
                <input type="text" name="first_name" placeholder="Họ" value={form.first_name} onChange={setField} />
                <input type="text" name="last_name" placeholder="Tên" value={form.last_name} onChange={setField} />
                <input type="text" name="phone" placeholder="Số điện thoại" value={form.phone} onChange={setField} />
                <input type="text" name="address" placeholder="Địa chỉ" value={form.address} onChange={setField} />
                <select name="id_country" value={form.id_country} onChange={setField} className="form-control" style={{ marginBottom: 10 }}>
                  <option value="">-- Chọn quốc gia --</option>
                  {countries.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
                <label>Avatar (dưới 1MB)</label>
                <input type="file" accept="image/*" onChange={(e) => setAvatar(e.target.files[0])} />
                <button type="submit" className="btn btn-default">Đăng ký</button>
              </form>
              <p style={{ marginTop: 15 }}>Đã có tài khoản? <Link to="/login">Đăng nhập</Link></p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
