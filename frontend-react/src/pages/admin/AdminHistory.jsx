// AdminHistory.jsx: lịch sử mua hàng: thống kê theo member + danh sách đơn
import { useEffect, useState } from 'react';
import { api } from '../../api';
import { dateTimeText, money } from '../../format';
import AdminSidebar from '../../components/AdminSidebar';
import Pagination from '../../components/Pagination';

export default function AdminHistory() {
  const [q, setQ] = useState('');
  const [search, setSearch] = useState('');
  const [userId, setUserId] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/admin/history/', { params: { q: search, user: userId, page } }).then(setData).catch((e) => setError(e.message));
  }, [search, userId, page]);

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3"><AdminSidebar /></div>
          <div className="col-sm-9">
            <h2 className="title text-center">Lịch sử mua hàng</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            {data && (
              <>
                <p>Tổng số đơn: <b>{data.summary.orders || 0}</b> - Tổng doanh thu: <b>${money(data.summary.total)}</b></p>
                <h4>Thống kê theo member</h4>
                <table className="table table-bordered">
                  <thead><tr><th>Member</th><th>Số đơn</th><th>Tổng tiền</th><th>Mua gần nhất</th><th></th></tr></thead>
                  <tbody>
                    {data.members.map((m) => (
                      <tr key={m.user_id || 'x'}>
                        <td>{m.user__username || '(user đã xóa)'}</td>
                        <td>{m.orders}</td>
                        <td>${money(m.total)}</td>
                        <td>{dateTimeText(m.last_order)}</td>
                        <td>{m.user_id && <a className="cursor" onClick={() => { setUserId(m.user_id); setPage(1); }}>Xem đơn</a>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <h4>Danh sách đơn hàng {userId && <a className="cursor" onClick={() => { setUserId(''); setPage(1); }}>[bỏ lọc member]</a>}</h4>
                <form className="form-inline" style={{ marginBottom: 15 }} onSubmit={(e) => { e.preventDefault(); setPage(1); setSearch(q); }}>
                  <input type="text" className="form-control" placeholder="Tên / email / sđt / username" value={q} onChange={(e) => setQ(e.target.value)} />{' '}
                  <button className="btn btn-default">Tìm</button>
                </form>
                <table className="table table-bordered">
                  <thead><tr><th>Mã</th><th>Ngày</th><th>Người mua</th><th>Liên hệ</th><th>Sản phẩm</th><th>Tổng</th></tr></thead>
                  <tbody>
                    {data.results.map((o) => (
                      <tr key={o.id}>
                        <td>#{o.id}</td>
                        <td>{dateTimeText(o.created_at)}</td>
                        <td>{o.name}<br /><small className="text-muted">{o.user_name}</small></td>
                        <td>{o.email}<br />{o.phone}</td>
                        <td style={{ whiteSpace: 'pre-line' }}>{o.items}</td>
                        <td>${money(o.price)}</td>
                      </tr>
                    ))}
                    {data.results.length === 0 && <tr><td colSpan="6" className="text-center">Chưa có đơn hàng.</td></tr>}
                  </tbody>
                </table>
                <Pagination data={data} onChange={setPage} />
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
