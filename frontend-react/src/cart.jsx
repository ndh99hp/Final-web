// cart.jsx: số sản phẩm trong giỏ (hiện ở menu) + hàm "Thêm vào giỏ" dùng chung cho mọi trang
import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from './api';
import { useAuth } from './auth';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user, isMember } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [count, setCount] = useState(0);
  const [toast, setToast] = useState(null);
  const timer = useRef(null);

  // đọc số sản phẩm trong giỏ từ server (chỉ member mới có giỏ hàng)
  const refresh = useCallback(async () => {
    if (!isMember) {
      setCount(0);
      return;
    }
    try {
      const data = await api('/cart/');
      setCount(data.cart_count);
    } catch (e) {
      // bỏ qua
    }
  }, [isMember]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // hiện thông báo nhỏ ở góc màn hình 2.5 giây
  function showToast(text, type = 'success') {
    setToast({ text, type });
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setToast(null), 2500);
  }

  // bấm "Thêm vào giỏ": chưa đăng nhập thì chuyển sang trang login
  async function addToCart(productId, qty = 1) {
    if (!user) {
      navigate('/login', { state: { from: location.pathname, message: 'Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng' } });
      return;
    }
    if (!isMember) {
      showToast('Tài khoản admin không mua hàng được', 'danger');
      return;
    }
    try {
      const data = await api('/cart/add/', { method: 'POST', body: { product_id: productId, qty } });
      setCount(data.cart_count);
      showToast(data.message);
    } catch (e) {
      showToast(e.message, 'danger');
    }
  }

  return (
    <CartContext.Provider value={{ count, setCount, refresh, addToCart }}>
      {children}
      {toast && (
        <div className={'alert alert-' + toast.type} style={{ position: 'fixed', top: 20, right: 20, zIndex: 9999, boxShadow: '0 2px 8px rgba(0,0,0,.3)' }}>
          {toast.text}
        </div>
      )}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}
