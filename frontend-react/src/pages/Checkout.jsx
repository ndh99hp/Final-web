// Checkout.jsx: thanh toán - điền sẵn thông tin từ tài khoản, bấm đặt hàng thì lưu lịch sử + gửi mail
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { useCart } from '../cart';
import { money } from '../format';
import Notice from '../components/Notice';

export default function Checkout() {
  const { setCount } = useCart();
  const [cart, setCart] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', phone: '' });
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    api('/cart/').then(setCart).catch((e) => setError(e.message));
    // điền sẵn từ thông tin tài khoản
    api('/account/').then((u) => {
      const fullName = ((u.first_name || '') + ' ' + (u.last_name || '')).trim();
      setForm({ name: fullName || u.username, email: u.email || '', phone: u.phone || '' });
    }).catch(() => {});
  }, []);

  function setField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSending(true);
    try {
      const d = await api('/checkout/', { method: 'POST', body: form });
      setResult(d);
      setCount(0);
    } catch (err) {
      setError(err.message);
    }
    setSending(false);
  }

  if (result) {
    return (
      <section><div className="container text-center">
        <h2 className="title">Đặt hàng thành công</h2>
        <Notice type="success">{result.message}</Notice>
        <p>{result.mail_sent ? 'Đã gửi mail xác nhận tới ' + result.order.email : 'Chưa gửi được mail xác nhận (kiểm tra cấu hình mail của Django).'}</p>
        <Link to="/orders" className="btn btn-primary">Xem lịch sử mua hàng</Link>{' '}
        <Link to="/shop" className="btn btn-default">Tiếp tục mua sắm</Link>
      </div></section>
    );
  }

  const empty = cart && cart.items.length === 0;
  return (
    <section>
      <div className="container">
        <h2 className="title text-center">Thanh toán</h2>
        <div className="row">
          <div className="col-sm-6">
            <form onSubmit={handleSubmit} className="box">
              <Notice>{error}</Notice>
              <label>Họ tên *</label>
              <input type="text" name="name" className="form-control" value={form.name} onChange={setField} maxLength="100" required style={{ marginBottom: 15 }} />
              <label>Email *</label>
              <input type="email" name="email" className="form-control" value={form.email} onChange={setField} required style={{ marginBottom: 15 }} />
              <label>Số điện thoại *</label>
              <input type="text" name="phone" className="form-control" value={form.phone} onChange={setField} required style={{ marginBottom: 20 }} />
              <button type="submit" className="btn btn-primary" disabled={sending || empty}>{sending ? 'Đang xử lý...' : 'Đặt hàng'}</button>
            </form>
          </div>
          <div className="col-sm-6">
            <div className="box">
              <h4>Đơn hàng của bạn</h4>
              {!cart && <p>Đang tải...</p>}
              {empty && <p>Giỏ hàng trống. <Link to="/shop">Chọn sản phẩm</Link></p>}
              {cart && cart.items.map((it) => (
                <p key={it.product_id}>{it.title} x {it.qty} <span className="pull-right">${money(it.total)}</span></p>
              ))}
              {cart && !empty && <h4>Tổng: <span className="pull-right" style={{ color: '#fe980f' }}>${money(cart.grand_total)}</span></h4>}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
