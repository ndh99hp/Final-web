// ResetPassword.jsx: trang mở từ link trong mail (/reset-password/:uid/:token)
import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api';
import Notice from '../components/Notice';

export default function ResetPassword() {
  const { uid, token } = useParams();
  const [form, setForm] = useState({ password: '', password2: '' });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      const d = await api('/reset-password/', { method: 'POST', body: { uid, token, ...form } });
      setMessage(d.message);
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
              <h2>Đặt lại mật khẩu</h2>
              <Notice>{error}</Notice>
              <Notice type="success">{message}</Notice>
              {message ? (
                <Link to="/login" className="btn btn-default">Đăng nhập</Link>
              ) : (
                <form onSubmit={handleSubmit}>
                  <input type="password" placeholder="Mật khẩu mới (từ 6 ký tự)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
                  <input type="password" placeholder="Nhập lại mật khẩu" value={form.password2} onChange={(e) => setForm({ ...form, password2: e.target.value })} required />
                  <button type="submit" className="btn btn-default">Đổi mật khẩu</button>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
