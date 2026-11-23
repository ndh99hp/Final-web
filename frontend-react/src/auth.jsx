// auth.jsx: lưu thông tin đăng nhập (token + user) để mọi trang dùng chung
import { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user'));
    } catch (e) {
      return null;
    }
  });

  // token hết hạn (api.js phát sự kiện) thì coi như đã đăng xuất
  useEffect(() => {
    const onExpired = () => setUser(null);
    window.addEventListener('auth-expired', onExpired);
    return () => window.removeEventListener('auth-expired', onExpired);
  }, []);

  function saveLogin(token, userData) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  }

  // cập nhật thông tin user (sau khi sửa account)
  function updateUser(userData) {
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  }

  async function logout() {
    try {
      await api('/logout/', { method: 'POST' }); // xóa token trên server
    } catch (e) {
      // lỗi cũng bỏ qua, vẫn xóa token ở trình duyệt
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  }

  const value = {
    user,
    isAdmin: !!user && user.role === 'admin',
    isMember: !!user && user.role === 'member',
    saveLogin,
    updateUser,
    logout,
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
