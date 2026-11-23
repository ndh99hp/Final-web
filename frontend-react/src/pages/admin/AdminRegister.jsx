// AdminRegister.jsx: tạo thêm superuser
import { useState } from 'react';
import { api } from '../../api';
import AdminSidebar from '../../components/AdminSidebar';
import Notice from '../../components/Notice';

const EMPTY = { username: '', email: '', password: '', password2: '' };

export default function AdminRegister() {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError(''); setMessage('');
    try {
      const d = await api('/admin/users/register-superuser/', { method: 'POST', body: form });
      setMessage(d.message);
      setForm(EMPTY);
    } catch (err) {
      setError(err.message);
    }
  }

  const set = (name) => (e) => setForm({ ...form, [name]: e.target.value });
  const gap = { marginBottom: 12 };
  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3"><AdminSidebar /></div>
          <div className="col-sm-9">
            <h2 className="title text-center">Tạo superuser</h2>
            <Notice>{error}</Notice>
            <Notice type="success">{message}</Notice>
            <form onSubmit={handleSubmit} className="box">
              <label>Tên đăng nhập *</label>
              <input type="text" className="form-control" value={form.username} onChange={set('username')} required style={gap} />
              <label>Email *</label>
              <input type="email" className="form-control" value={form.email} onChange={set('email')} required style={gap} />
              <label>Mật khẩu *</label>
              <input type="password" className="form-control" value={form.password} onChange={set('password')} required style={gap} />
              <label>Nhập lại mật khẩu *</label>
              <input type="password" className="form-control" value={form.password2} onChange={set('password2')} required style={{ marginBottom: 20 }} />
              <button type="submit" className="btn btn-primary">Tạo superuser</button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
