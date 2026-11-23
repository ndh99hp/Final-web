// Layout.jsx: khung chung của mọi trang (header + nội dung + footer)
import { Outlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import Header from './Header';
import Footer from './Footer';

export default function Layout() {
  const { pathname } = useLocation();
  // sang trang khác thì cuộn lên đầu
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return (
    <>
      <Header />
      <Outlet />
      <Footer />
    </>
  );
}
