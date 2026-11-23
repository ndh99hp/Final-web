// ForgotPassword.jsx: nhập email để nhận link đặt lại mật khẩu
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import Notice from '../components/Notice';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(''); setMessage(''); setSending(true);
    try {
      const d = await api('/forgot-password/', { method: 'POST', body: { email } });
      setMessage(d.message);
    } catch (err) {
      setError(err.message);
    }
    setSending(false);
  }

  return (
    <section id="form">
      <div className="container">
        <div className="row">
          <div className="col-sm-4 col-sm-offset-4">
            <div className="login-form">
              <h2>Quên mật khẩu</h2>
              <Notice>{error}</Notice>
              <Notice type="success">{message}</Notice>
              <form onSubmit={handleSubmit}>
                <input type="email" placeholder="Email đã đăng ký" value={email} onChange={(e) => setEmail(e.target.value)} required />
                <button type="submit" className="btn btn-default" disabled={sending}>{sending ? 'Đang gửi...' : 'Gửi link đặt lại mật khẩu'}</button>
              </form>
              <p style={{ marginTop: 15 }}><Link to="/login">Quay lại đăng nhập</Link></p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
