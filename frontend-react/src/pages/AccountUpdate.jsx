// AccountUpdate.jsx: cập nhật thông tin tài khoản member
import { useEffect, useState } from 'react';
import { api } from '../api';
import { useAuth } from '../auth';
import AccountSidebar from '../components/AccountSidebar';
import Notice from '../components/Notice';

export default function AccountUpdate() {
  const { updateUser } = useAuth();
  const [countries, setCountries] = useState([]);
  const [form, setForm] = useState(null);
  const [avatarUrl, setAvatarUrl] = useState('');
  const [avatar, setAvatar] = useState(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    api('/countries/').then(setCountries).catch(() => {});
    api('/account/').then((u) => {
      setAvatarUrl(u.avatar);
      setForm({
        username: u.username, email: u.email || '', first_name: u.first_name || '', last_name: u.last_name || '',
        phone: u.phone || '', address: u.address || '', id_country: u.id_country ? String(u.id_country) : '', password: '',
      });
    }).catch((e) => setError(e.message));
  }, []);

  function setField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(''); setMessage('');
    const data = new FormData();
    Object.keys(form).forEach((k) => { if (k !== 'username') data.append(k, form[k]); });
    if (avatar) data.append('avatar', avatar);
    try {
      const d = await api('/account/update/', { method: 'PUT', body: data });
      updateUser(d.user);
      setAvatarUrl(d.user.avatar);
      setForm({ ...form, password: '' });
      setMessage(d.message);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3"><AccountSidebar /></div>
          <div className="col-sm-9">
            <h2 className="title text-center">Cập nhật thông tin</h2>
            <Notice>{error}</Notice>
            <Notice type="success">{message}</Notice>
            {form && (
              <form onSubmit={handleSubmit} className="box">
                <div className="row">
                  <div className="col-sm-8">
                    <label>Tên đăng nhập</label>
                    <input type="text" className="form-control" value={form.username} disabled style={{ marginBottom: 12 }} />
                    <label>Email *</label>
                    <input type="email" name="email" className="form-control" value={form.email} onChange={setField} required style={{ marginBottom: 12 }} />
                    <label>Họ</label>
                    <input type="text" name="first_name" className="form-control" value={form.first_name} onChange={setField} style={{ marginBottom: 12 }} />
                    <label>Tên</label>
                    <input type="text" name="last_name" className="form-control" value={form.last_name} onChange={setField} style={{ marginBottom: 12 }} />
                    <label>Số điện thoại</label>
                    <input type="text" name="phone" className="form-control" value={form.phone} onChange={setField} style={{ marginBottom: 12 }} />
                    <label>Địa chỉ</label>
                    <input type="text" name="address" className="form-control" value={form.address} onChange={setField} style={{ marginBottom: 12 }} />
                    <label>Quốc gia</label>
                    <select name="id_country" className="form-control" value={form.id_country} onChange={setField} style={{ marginBottom: 12 }}>
                      <option value="">-- Chọn quốc gia --</option>
                      {countries.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                    <label>Mật khẩu mới <small className="text-muted">(bỏ trống nếu không đổi)</small></label>
                    <input type="password" name="password" className="form-control" value={form.password} onChange={setField} style={{ marginBottom: 12 }} />
                  </div>
                  <div className="col-sm-4 text-center">
                    {avatarUrl && <img src={avatarUrl} alt="avatar" style={{ width: 150, height: 150, objectFit: 'cover', borderRadius: '50%', marginBottom: 10 }} />}
                    <input type="file" accept="image/*" onChange={(e) => setAvatar(e.target.files[0])} />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary">Lưu thay đổi</button>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
