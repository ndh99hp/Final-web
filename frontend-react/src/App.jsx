// App.jsx: khai báo các đường dẫn (route) của web
import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import { RequireAdmin, RequireMember } from './components/Guards';

import Home from './pages/Home';
import Shop from './pages/Shop';
import ProductDetail from './pages/ProductDetail';
import SearchAdvanced from './pages/SearchAdvanced';
import BlogList from './pages/BlogList';
import BlogDetail from './pages/BlogDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import AccountUpdate from './pages/AccountUpdate';
import MyProducts from './pages/MyProducts';
import ProductEdit from './pages/ProductEdit';
import Contact from './pages/Contact';
import NotFound from './pages/NotFound';
import AdminLogin from './pages/admin/AdminLogin';
import AdminUsers from './pages/admin/AdminUsers';
import AdminEditUser from './pages/admin/AdminEditUser';
import AdminRegister from './pages/admin/AdminRegister';
import AdminProducts from './pages/admin/AdminProducts';
import AdminHistory from './pages/admin/AdminHistory';

export default function App() {
  const member = (page) => <RequireMember>{page}</RequireMember>;
  const admin = (page) => <RequireAdmin>{page}</RequireAdmin>;
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* công khai */}
        <Route path="/" element={<Home />} />
        <Route path="/shop" element={<Shop />} />
        <Route path="/shop/:id" element={<ProductDetail />} />
        <Route path="/search-advanced" element={<SearchAdvanced />} />
        <Route path="/blog" element={<BlogList />} />
        <Route path="/blog/:slug" element={<BlogDetail />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />

        {/* member */}
        <Route path="/cart" element={member(<Cart />)} />
        <Route path="/checkout" element={member(<Checkout />)} />
        <Route path="/orders" element={member(<Orders />)} />
        <Route path="/account" element={member(<AccountUpdate />)} />
        <Route path="/account/my-product" element={member(<MyProducts />)} />
        <Route path="/account/add-product" element={member(<ProductEdit />)} />
        <Route path="/account/edit-product/:id" element={member(<ProductEdit />)} />

        {/* admin */}
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/users" element={admin(<AdminUsers />)} />
        <Route path="/admin/users/new" element={admin(<AdminRegister />)} />
        <Route path="/admin/users/:id/edit" element={admin(<AdminEditUser />)} />
        <Route path="/admin/products" element={admin(<AdminProducts />)} />
        <Route path="/admin/products/:id/edit" element={admin(<ProductEdit admin />)} />
        <Route path="/admin/history" element={admin(<AdminHistory />)} />

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
