// AdminEditUser.jsx: sửa thông tin member (khóa / mở khóa, đổi mật khẩu)
// Thông tin user được truyền từ danh sách qua location.state; nếu mở thẳng link thì lấy lại từ danh sách API
import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { api } from '../../api';
import AdminSidebar from '../../components/AdminSidebar';
import Notice from '../../components/Notice';

export default function AdminEditUser() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [countries, setCountries] = useState([]);
  const [form, setForm] = useState(null);
  const [error, setError] = useState('');

  function fill(u) {
    setForm({
      username: u.username, email: u.email || '', first_name: u.first_name || '', last_name: u.last_name || '',
      phone: u.phone || '', address: u.address || '', id_country: u.id_country ? String(u.id_country) : '',
      is_active: u.is_active ? '1' : '0', password: '',
    });
  }

  useEffect(() => {
    api('/countries/').then(setCountries).catch(() => {});
    if (location.state && location.state.user) {
      fill(location.state.user);
    } else {
      // tìm user trong danh sách (tối đa vài trang)
      api('/admin/users/', { params: { role: 'member' } }).then((d) => {
        const u = d.results.find((x) => String(x.id) === id);
        if (u) fill(u); else setError('Không tìm thấy user (hãy mở từ danh sách user)');
      }).catch((e) => setError(e.message));
    }
  }, [id]);

  function setField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    const body = { ...form };
    delete body.username;
    if (!body.password) delete body.password;
    try {
      const d = await api('/admin/users/update/' + id + '/', { method: 'PUT', body });
      navigate('/admin/users', { state: { message: d.message } });
    } catch (err) {
      setError(err.message);
    }
  }

  const gap = { marginBottom: 12 };
  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3"><AdminSidebar /></div>
          <div className="col-sm-9">
            <h2 className="title text-center">Sửa user</h2>
            <Notice>{error}</Notice>
            {form && (
              <form onSubmit={handleSubmit} className="box">
                <label>Tên đăng nhập</label>
                <input type="text" className="form-control" value={form.username} disabled style={gap} />
                <label>Email *</label>
                <input type="email" name="email" className="form-control" value={form.email} onChange={setField} required style={gap} />
                <div className="row">
                  <div className="col-sm-6"><label>Họ</label><input type="text" name="first_name" className="form-control" value={form.first_name} onChange={setField} style={gap} /></div>
                  <div className="col-sm-6"><label>Tên</label><input type="text" name="last_name" className="form-control" value={form.last_name} onChange={setField} style={gap} /></div>
                </div>
                <label>Số điện thoại</label>
                <input type="text" name="phone" className="form-control" value={form.phone} onChange={setField} style={gap} />
                <label>Địa chỉ</label>
                <input type="text" name="address" className="form-control" value={form.address} onChange={setField} style={gap} />
                <label>Quốc gia</label>
                <select name="id_country" className="form-control" value={form.id_country} onChange={setField} style={gap}>
                  <option value="">-- Chọn quốc gia --</option>
                  {countries.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
                <label>Trạng thái</label>
                <select name="is_active" className="form-control" value={form.is_active} onChange={setField} style={gap}>
                  <option value="1">Hoạt động</option>
                  <option value="0">Khóa</option>
                </select>
                <label>Mật khẩu mới <small className="text-muted">(bỏ trống = giữ nguyên)</small></label>
                <input type="password" name="password" className="form-control" value={form.password} onChange={setField} style={{ marginBottom: 20 }} />
                <button type="submit" className="btn btn-primary">Lưu</button>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
