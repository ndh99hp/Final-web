// AdminLogin.jsx: đăng nhập admin (chỉ superuser)
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../../api';
import { useAuth } from '../../auth';
import Notice from '../../components/Notice';

export default function AdminLogin() {
  const { saveLogin } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      const d = await api('/admin/login/', { method: 'POST', body: form });
      saveLogin(d.token, d.user);
      navigate('/admin/users');
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section id="form">
      <div className="container">
        <div className="row">
          <div className="col-sm-4 col-sm-offset-4">
            <div className="login-form">
              <h2>Đăng nhập quản trị</h2>
              <Notice>{error}</Notice>
              <form onSubmit={handleSubmit}>
                <input type="text" placeholder="Tên đăng nhập admin" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
                <input type="password" placeholder="Mật khẩu" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
                <button type="submit" className="btn btn-default">Đăng nhập</button>
              </form>
              <p style={{ marginTop: 15 }}><Link to="/login">Đăng nhập thành viên</Link></p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
