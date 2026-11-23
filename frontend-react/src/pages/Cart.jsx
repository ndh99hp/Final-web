// Cart.jsx: giỏ hàng (lưu trong database)
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { useCart } from '../cart';
import { DEFAULT_IMAGE, money } from '../format';

export default function Cart() {
  const { setCount } = useCart();
  const [cart, setCart] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/cart/').then((d) => { setCart(d); setCount(d.cart_count); }).catch((e) => setError(e.message));
  }, []);

  // action: up (+1), down (-1), delete (xóa dòng)
  async function change(productId, action) {
    try {
      const d = await api('/cart/update/', { method: 'PUT', body: { product_id: productId, action } });
      setCart(d);
      setCount(d.cart_count);
    } catch (e) {
      setError(e.message);
    }
  }

  if (!cart) return <section><div className="container">{error ? <div className="alert alert-danger">{error}</div> : <p>Đang tải...</p>}</div></section>;

  return (
    <section id="cart_items">
      <div className="container">
        <h2 className="title text-center">Giỏ hàng</h2>
        {error && <div className="alert alert-danger">{error}</div>}
        {cart.items.length === 0 ? (
          <p className="text-center">Giỏ hàng đang trống. <Link to="/shop">Tiếp tục mua sắm</Link></p>
        ) : (
          <>
            <div className="table-responsive cart_info">
              <table className="table table-condensed">
                <thead>
                  <tr className="cart_menu">
                    <td className="image">Sản phẩm</td>
                    <td className="description"></td>
                    <td className="price">Giá</td>
                    <td className="quantity">Số lượng</td>
                    <td className="total">Thành tiền</td>
                    <td></td>
                  </tr>
                </thead>
                <tbody>
                  {cart.items.map((it) => (
                    <tr key={it.product_id}>
                      <td className="cart_product"><Link to={'/shop/' + it.product_id}><img src={it.image || DEFAULT_IMAGE} alt="" style={{ width: 90, height: 90, objectFit: 'cover' }} /></Link></td>
                      <td className="cart_description"><h4><Link to={'/shop/' + it.product_id}>{it.title}</Link></h4><p>Mã: {it.product_id}</p></td>
                      <td className="cart_price"><p>${money(it.price)}</p></td>
                      <td className="cart_quantity">
                        <div className="cart_quantity_button">
                          <a className="cart_quantity_up cursor" onClick={() => change(it.product_id, 'up')}> + </a>
                          <input className="cart_quantity_input" type="text" value={it.qty} readOnly autoComplete="off" size="2" />
                          <a className="cart_quantity_down cursor" onClick={() => change(it.product_id, 'down')}> - </a>
                        </div>
                      </td>
                      <td className="cart_total"><p className="cart_total_price">${money(it.total)}</p></td>
                      <td className="cart_delete"><a className="cart_quantity_delete cursor" onClick={() => change(it.product_id, 'delete')}><i className="fa fa-times"></i></a></td>
                    </tr>
                  ))}
                  <tr>
                    <td colSpan="4" className="text-right"><b>Tổng cộng:</b></td>
                    <td colSpan="2"><span style={{ fontSize: 20, color: '#fe980f' }}>${money(cart.grand_total)}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="text-right">
              <Link to="/shop" className="btn btn-default">Tiếp tục mua</Link>{' '}
              <Link to="/checkout" className="btn btn-primary">Thanh toán</Link>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
