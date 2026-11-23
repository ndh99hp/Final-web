// AdminUsers.jsx: danh sách user (tìm, lọc quyền, sửa, xóa)
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { api } from '../../api';
import { dateText } from '../../format';
import AdminSidebar from '../../components/AdminSidebar';
import Notice from '../../components/Notice';
import Pagination from '../../components/Pagination';

export default function AdminUsers() {
  const location = useLocation();
  const [q, setQ] = useState('');
  const [role, setRole] = useState('');
  const [search, setSearch] = useState({ q: '', role: '' });
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState((location.state && location.state.message) || '');

  function load() {
    api('/admin/users/', { params: { q: search.q, role: search.role, page } }).then(setData).catch((e) => setError(e.message));
  }
  useEffect(load, [search, page]);

  async function handleDelete(u) {
    if (!window.confirm('Xóa user "' + u.username + '" và toàn bộ sản phẩm của user này?')) return;
    try {
      const d = await api('/admin/users/delete/' + u.id + '/', { method: 'DELETE' });
      setMessage(d.message);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3"><AdminSidebar /></div>
          <div className="col-sm-9">
            <h2 className="title text-center">Danh sách user</h2>
            <Notice type="success">{message}</Notice>
            <Notice>{error}</Notice>
            <form className="form-inline" style={{ marginBottom: 15 }} onSubmit={(e) => { e.preventDefault(); setPage(1); setSearch({ q, role }); }}>
              <input type="text" className="form-control" placeholder="Username / email" value={q} onChange={(e) => setQ(e.target.value)} />{' '}
              <select className="form-control" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="">Tất cả</option>
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>{' '}
              <button className="btn btn-default">Tìm</button>
            </form>
            {data && data.results.length === 0 && <p className="text-center">Không có user nào.</p>}
            {data && data.results.length > 0 && (
              <table className="table table-bordered">
                <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Quyền</th><th>Số SP</th><th>Trạng thái</th><th>Ngày tạo</th><th></th></tr></thead>
                <tbody>
                  {data.results.map((u) => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td>{u.username}</td>
                      <td>{u.email}</td>
                      <td>{u.role === 'admin' ? <span className="label label-danger">Admin</span> : <span className="label label-info">Member</span>}</td>
                      <td>{u.total_products}</td>
                      <td>{u.is_active ? 'Hoạt động' : <b className="text-danger">Bị khóa</b>}</td>
                      <td>{dateText(u.date_joined)}</td>
                      <td>
                        {u.role === 'member' && (
                          <>
                            <Link to={'/admin/users/' + u.id + '/edit'} state={{ user: u }} className="btn btn-xs btn-default">Sửa</Link>{' '}
                            <button className="btn btn-xs btn-danger" onClick={() => handleDelete(u)}>Xóa</button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <Pagination data={data} onChange={setPage} />
          </div>
        </div>
      </div>
    </section>
  );
}
