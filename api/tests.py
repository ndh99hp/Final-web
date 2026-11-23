# api/tests.py: test tự động cho API. Chạy:  python manage.py test api
import shutil
import tempfile
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from blog.models import Blog
from product.models import Brand, Category, Product
from users.models import Country, User

TEMP_MEDIA = tempfile.mkdtemp()


def make_image(name='a.png', size=100):
    return SimpleUploadedFile(name, b'x' * size, content_type='image/png')


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ApiTestBase(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.country = Country.objects.create(name='Vietnam')
        self.category = Category.objects.create(name='Ao')
        self.brand = Brand.objects.create(name='Gucci')
        self.admin = User.objects.create_user('boss', 'boss@x.com', 'secret123', is_superuser=True, is_staff=True)
        self.member = User.objects.create_user('mem1', 'mem1@x.com', 'secret123')
        self.member2 = User.objects.create_user('mem2', 'mem2@x.com', 'secret123')

    # đăng nhập bằng API, trả về token
    def token_of(self, username, url='/api/login/'):
        res = self.client.post(url, {'username': username, 'password': 'secret123'}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        return res.json()['token']

    # gọi API với token của 1 user
    def as_user(self, username, url='/api/login/'):
        token = self.token_of(username, url)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def as_admin(self):
        self.as_user('boss', '/api/admin/login/')

    def anonymous(self):
        self.client.credentials()

    def new_product(self, author=None, **kwargs):
        data = {'title': 'Ao thun', 'price': '100.00', 'category': self.category,
                'brand': self.brand, 'author': author or self.member}
        data.update(kwargs)
        return Product.objects.create(**data)


class AuthTests(ApiTestBase):
    def test_register_login_account(self):
        res = self.client.post('/api/register/', {
            'username': 'newbie', 'email': 'new@x.com', 'password': 'abcdef', 'password2': 'abcdef',
            'first_name': 'A', 'last_name': 'B', 'id_country': self.country.id,
            'avatar': make_image('av.png')}, format='multipart')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertIn('token', res.json())
        self.assertEqual(res.json()['user']['role'], 'member')
        self.assertTrue(res.json()['user']['avatar'].startswith('http'))
        self.assertEqual(len(mail.outbox), 1)                       # mail chào mừng
        user = User.objects.get(username='newbie')
        self.assertFalse(user.is_superuser or user.is_staff)

        # đăng nhập + xem + sửa account
        res = self.client.post('/api/login/', {'username': 'newbie', 'password': 'abcdef'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + res.json()['token'])
        self.assertEqual(self.client.get('/api/account/').json()['email'], 'new@x.com')
        res = self.client.put('/api/account/update/', {'phone': '0123456789', 'password': 'newpass1'}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json()['user']['phone'], '0123456789')
        self.assertEqual(self.client.put('/api/account/update/', {'email': 'bad'}, format='json').status_code, 400)
        # logout xóa token
        self.assertEqual(self.client.post('/api/logout/').status_code, 200)
        self.assertEqual(self.client.get('/api/account/').status_code, 401)
        # đổi mật khẩu có hiệu lực
        self.anonymous()
        self.assertEqual(self.client.post('/api/login/', {'username': 'newbie', 'password': 'newpass1'}, format='json').status_code, 200)

    def test_register_errors(self):
        base = {'username': 'u', 'email': 'a@x.com', 'password': 'abcdef', 'password2': 'abcdef'}
        for change in ({'username': 'mem1'}, {'email': 'bad'}, {'password': '123', 'password2': '123'},
                       {'password2': 'zzzzzz'}, {'id_country': 999}):
            data = dict(base)
            data.update(change)
            res = self.client.post('/api/register/', data, format='json')
            self.assertEqual(res.status_code, 400, change)
            self.assertIn('error', res.json())

    def test_login_roles(self):
        # sai mật khẩu
        self.assertEqual(self.client.post('/api/login/', {'username': 'mem1', 'password': 'x'}, format='json').status_code, 400)
        # admin không đăng nhập được ở login của member, member không vào được admin/login
        self.assertEqual(self.client.post('/api/login/', {'username': 'boss', 'password': 'secret123'}, format='json').status_code, 403)
        self.assertEqual(self.client.post('/api/admin/login/', {'username': 'mem1', 'password': 'secret123'}, format='json').status_code, 403)
        self.assertEqual(self.client.post('/api/admin/login/', {'username': 'boss', 'password': 'secret123'}, format='json').status_code, 200)

    def test_permissions(self):
        self.assertEqual(self.client.get('/api/account/').status_code, 401)       # chưa đăng nhập
        self.assertEqual(self.client.get('/api/cart/').status_code, 401)
        self.assertEqual(self.client.get('/api/admin/users/').status_code, 401)
        self.as_user('mem1')
        self.assertEqual(self.client.get('/api/admin/users/').status_code, 403)   # member không vào được admin
        self.as_admin()
        self.assertEqual(self.client.get('/api/account/').status_code, 403)       # admin không vào API member
        self.assertEqual(self.client.get('/api/cart/').status_code, 403)
        self.assertEqual(self.client.get('/api/admin/users/').status_code, 200)
        # token sai
        self.client.credentials(HTTP_AUTHORIZATION='Token abc')
        self.assertEqual(self.client.get('/api/account/').status_code, 401)

    def test_forgot_reset_password(self):
        self.assertEqual(self.client.post('/api/forgot-password/', {'email': ''}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/forgot-password/', {'email': 'no@x.com'}, format='json').status_code, 404)
        self.assertEqual(self.client.post('/api/forgot-password/', {'email': 'boss@x.com'}, format='json').status_code, 404)   # admin không dùng
        res = self.client.post('/api/forgot-password/', {'email': 'mem1@x.com'}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        body = mail.outbox[-1].body
        link = body.split(': ')[-1].strip()
        self.assertTrue(link.startswith('http://localhost:3000/reset-password/'))
        uid, token = link.split('/')[-2:]
        self.assertEqual(self.client.post('/api/reset-password/', {'uid': uid, 'token': 'bad', 'password': 'abcdef', 'password2': 'abcdef'}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/reset-password/', {'uid': uid, 'token': token, 'password': '123', 'password2': '123'}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/reset-password/', {'uid': uid, 'token': token, 'password': 'abcdef', 'password2': 'zzz'}, format='json').status_code, 400)
        res = self.client.post('/api/reset-password/', {'uid': uid, 'token': token, 'password': 'abcdef', 'password2': 'abcdef'}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(self.client.post('/api/login/', {'username': 'mem1', 'password': 'abcdef'}, format='json').status_code, 200)
        # link chỉ dùng được 1 lần
        res = self.client.post('/api/reset-password/', {'uid': uid, 'token': token, 'password': 'qwerty1', 'password2': 'qwerty1'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_countries(self):
        res = self.client.get('/api/countries/')
        self.assertEqual(res.json(), [{'id': self.country.id, 'name': 'Vietnam'}])


class ProductTests(ApiTestBase):
    def test_public_lists(self):
        for i in range(12):
            self.new_product(title='Item %02d' % i, price=str(10 * (i + 1)))
        self.new_product(title='Sale shoes', price='500.00', status=1, sale='50.00')
        self.assertEqual(self.client.get('/api/home/').json()['results'][0]['title'], 'Sale shoes')
        self.assertEqual(len(self.client.get('/api/home/').json()['results']), 6)

        res = self.client.get('/api/products/').json()
        self.assertEqual(res['count'], 13)
        self.assertEqual(len(res['results']), 9)
        self.assertEqual(res['total_pages'], 2)
        self.assertEqual(len(self.client.get('/api/products/?page=2').json()['results']), 4)
        self.assertEqual(len(self.client.get('/api/products/?page=999').json()['results']), 4)    # trang quá lớn -> trang cuối
        self.assertEqual(len(self.client.get('/api/products/?page=abc').json()['results']), 9)

        # lọc theo giá hiện hành (sale shoes giá hiện hành = 50)
        res = self.client.get('/api/products/?price=45,55').json()
        self.assertEqual([p['title'] for p in res['results']], ['Sale shoes', 'Item 04'])   # mới nhất đứng trước
        self.assertEqual(self.client.get('/api/products/?price=NaN,5').json()['count'], 13)   # sai định dạng: bỏ qua
        self.assertEqual(self.client.get('/api/products/?price=abc').json()['count'], 13)
        # từ khóa, sắp xếp
        self.assertEqual(self.client.get('/api/products/?q=shoes').json()['count'], 1)
        res = self.client.get('/api/products/?sort=price_desc').json()['results']
        self.assertEqual(res[0]['title'], 'Item 11')                  # 120 là cao nhất theo giá hiện hành
        res = self.client.get('/api/products/?sort=price_asc').json()['results']
        self.assertEqual(res[0]['title'], 'Item 00')
        self.assertEqual(self.client.get('/api/products/?category=' + str(self.category.id)).json()['count'], 13)
        self.assertEqual(self.client.get('/api/products/?category=abc&brand=²').json()['count'], 13)

        # filters
        f = self.client.get('/api/filters/').json()
        self.assertEqual(f['categories'][0]['total'], 13)
        self.assertEqual(f['slider_max'], 501)
        self.assertEqual(len(f['price_ranges']), 6)

        # tìm kiếm nâng cao
        res = self.client.get('/api/products/search/?price=10-50').json()
        self.assertEqual(res['count'], 6)       # Item 00..04 (10..50) + Sale shoes (giá hiện hành 50)
        res = self.client.get('/api/products/search/?status=1').json()
        self.assertEqual(res['count'], 1)
        self.assertEqual(self.client.get('/api/products/search/?name=item&status=0&brand=%d' % self.brand.id).json()['count'], 12)
        self.assertEqual(self.client.get('/api/products/search/').json()['count'], 13)
        self.assertEqual(self.client.get('/api/products/search/?price=1-2').json()['count'], 13)   # khoảng giá lạ: bỏ qua

    def test_detail(self):
        p = self.new_product(images='["products/a.jpg", "products/b.jpg"]')
        for i in range(7):
            self.new_product(title='Rel %d' % i)
        other = Category.objects.create(name='Quan')
        self.new_product(title='Khac loai', category=other)
        res = self.client.get('/api/products/%d/' % p.id).json()
        self.assertEqual(res['product']['title'], 'Ao thun')
        self.assertEqual(len(res['product']['images']), 2)
        self.assertTrue(res['product']['image'].endswith('/media/products/a.jpg'))
        self.assertEqual(res['product']['category_name'], 'Ao')
        self.assertEqual(res['product']['author_name'], 'mem1')
        self.assertEqual(len(res['related']), 6)
        self.assertNotIn('Khac loai', [r['title'] for r in res['related']])
        self.assertEqual(self.client.get('/api/products/99999/').status_code, 404)

    def test_member_crud(self):
        self.anonymous()
        self.assertEqual(self.client.post('/api/my-products/create/', {}, format='multipart').status_code, 401)
        self.as_user('mem1')
        data = {'title': 'Giay', 'price': '99.5', 'category': self.category.id, 'brand': self.brand.id,
                'status': '1', 'sale': '50', 'company': 'ACME', 'detail': 'tot',
                'images': [make_image('x1.png'), make_image('x2.png')]}
        res = self.client.post('/api/my-products/create/', data, format='multipart')
        self.assertEqual(res.status_code, 201, res.content)
        pid = res.json()['id']
        self.assertEqual(len(res.json()['images']), 2)
        self.assertEqual(res.json()['final_price'], 50.0)
        self.assertEqual(res.json()['price'], 99.5)
        product = Product.objects.get(id=pid)
        self.assertEqual(product.author, self.member)
        names = product.get_images()

        # lỗi dữ liệu
        bad = dict(data)
        for change, text in (({'title': ''}, 'tên'), ({'price': '0'}, 'Giá'), ({'price': 'abc'}, 'Giá'),
                             ({'sale': '200'}, 'sale'), ({'status': '5'}, 'Trạng'), ({'category': '999'}, 'Danh mục'),
                             ({'images': [make_image('a.png') for i in range(4)]}, 'tối đa'),
                             ({'images': [SimpleUploadedFile('a.txt', b'x', content_type='text/plain')]}, 'hình ảnh'),
                             ({'images': [make_image('big.png', 1024 * 1024)]}, '1MB')):
            bad = dict(data)
            bad.update(change)
            res = self.client.post('/api/my-products/create/', bad, format='multipart')
            self.assertEqual(res.status_code, 400, change)
            self.assertIn('error', res.json())
        self.assertEqual(Product.objects.count(), 1)

        # danh sách của tôi
        self.assertEqual(self.client.get('/api/my-products/').json()['count'], 1)
        self.assertEqual(self.client.get('/api/my-products/?q=zzz').json()['count'], 0)

        # sửa: xóa 1 hình cũ, thêm 1 hình mới
        upd = {'title': 'Giay moi', 'price': '120', 'status': '0', 'delete_images': [names[0]], 'images': [make_image('x3.png')]}
        res = self.client.put('/api/my-products/update/%d/' % pid, upd, format='multipart')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json()['title'], 'Giay moi')
        self.assertEqual(res.json()['sale'], 0)
        product.refresh_from_db()
        self.assertEqual(len(product.get_images()), 2)
        self.assertNotIn(names[0], product.get_images())
        # quá 3 hình
        upd = {'title': 'x', 'price': '5', 'images': [make_image('p1.png'), make_image('p2.png')]}
        self.assertEqual(self.client.put('/api/my-products/update/%d/' % pid, upd, format='multipart').status_code, 400)
        # sửa bằng JSON (không hình) cũng được
        res = self.client.put('/api/my-products/update/%d/' % pid, {'title': 'Json', 'price': 10, 'status': 0}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(len(res.json()['images']), 2)

        # member khác không sửa / xóa được
        self.as_user('mem2')
        self.assertEqual(self.client.put('/api/my-products/update/%d/' % pid, {'title': 'hack', 'price': '1'}, format='json').status_code, 404)
        self.assertEqual(self.client.delete('/api/my-products/delete/%d/' % pid).status_code, 404)
        # chủ xóa
        self.as_user('mem1')
        res = self.client.delete('/api/my-products/delete/%d/' % pid)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Product.objects.filter(id=pid).exists())
        self.assertEqual(self.client.delete('/api/my-products/delete/%d/' % pid).status_code, 404)

    def test_admin_cannot_use_member_product_api(self):
        self.as_admin()
        res = self.client.post('/api/my-products/create/', {'title': 'x', 'price': '1'}, format='multipart')
        self.assertEqual(res.status_code, 403)


class CartTests(ApiTestBase):
    def test_cart_checkout(self):
        p1 = self.new_product(title='P1', price='10.00')
        p2 = self.new_product(title='P2', price='100.00', status=1, sale='30.00')
        self.as_user('mem1')
        self.assertEqual(self.client.get('/api/cart/').json()['cart_count'], 0)
        self.assertEqual(self.client.post('/api/checkout/', {'name': 'A', 'email': 'a@x.com', 'phone': '0123456789'}, format='json').status_code, 400)  # giỏ trống

        res = self.client.post('/api/cart/add/', {'product_id': p1.id, 'qty': 2}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.json()['cart_count'], 1)
        res = self.client.post('/api/cart/add/', {'product_id': p1.id}, format='json')       # thêm lần nữa: cộng dồn
        self.assertEqual(res.status_code, 200)
        self.client.post('/api/cart/add/', {'product_id': p2.id, 'qty': '1'}, format='json')
        cart = self.client.get('/api/cart/').json()
        self.assertEqual(cart['cart_count'], 2)
        self.assertEqual(cart['items'][0]['qty'], 3)
        self.assertEqual(cart['items'][0]['total'], 30.0)
        self.assertEqual(cart['items'][1]['price'], 30.0)              # giá sale
        self.assertEqual(cart['grand_total'], 60.0)
        self.assertEqual(self.client.post('/api/cart/add/', {'product_id': 'abc'}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/cart/add/', {'product_id': 99999}, format='json').status_code, 404)
        self.client.post('/api/cart/add/', {'product_id': p2.id, 'qty': 500}, format='json')    # qty sai -> lấy 1
        self.assertEqual(self.client.get('/api/cart/').json()['items'][1]['qty'], 2)

        # +, -, xóa
        res = self.client.put('/api/cart/update/', {'product_id': p2.id, 'action': 'up'}, format='json').json()
        self.assertEqual(res['items'][1]['qty'], 3)
        res = self.client.put('/api/cart/update/', {'product_id': p2.id, 'action': 'down'}, format='json').json()
        self.assertEqual(res['items'][1]['qty'], 2)
        for i in range(5):
            res = self.client.put('/api/cart/update/', {'product_id': p2.id, 'action': 'down'}, format='json').json()
        self.assertEqual(res['items'][1]['qty'], 1)                    # không xuống dưới 1
        self.assertEqual(self.client.put('/api/cart/update/', {'product_id': p2.id, 'action': 'x'}, format='json').status_code, 400)
        self.assertEqual(self.client.put('/api/cart/update/', {'product_id': 99999, 'action': 'up'}, format='json').status_code, 404)
        res = self.client.put('/api/cart/update/', {'product_id': p2.id, 'action': 'delete'}, format='json').json()
        self.assertEqual(res['cart_count'], 1)

        # giỏ của member khác tách riêng
        self.as_user('mem2')
        self.assertEqual(self.client.get('/api/cart/').json()['cart_count'], 0)
        self.as_user('mem1')

        # checkout: lỗi dữ liệu
        for change in ({'name': ''}, {'email': 'bad'}, {'phone': '12'}, {'phone': 'abc12345'}):
            data = {'name': 'An', 'email': 'a@x.com', 'phone': '0123456789'}
            data.update(change)
            self.assertEqual(self.client.post('/api/checkout/', data, format='json').status_code, 400, change)
        mail.outbox.clear()
        res = self.client.post('/api/checkout/', {'name': 'An', 'email': 'a@x.com', 'phone': '0123456789'}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.json()['order']['price'], 30.0)
        self.assertIn('P1 x3', res.json()['order']['items'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['a@x.com'])
        self.assertEqual(self.client.get('/api/cart/').json()['cart_count'], 0)     # giỏ đã trống
        orders = self.client.get('/api/orders/').json()
        self.assertEqual(orders['count'], 1)
        self.as_user('mem2')
        self.assertEqual(self.client.get('/api/orders/').json()['count'], 0)

    def test_cart_removed_with_product(self):
        p = self.new_product()
        self.as_user('mem1')
        self.client.post('/api/cart/add/', {'product_id': p.id}, format='json')
        p.delete()
        self.assertEqual(self.client.get('/api/cart/').json()['cart_count'], 0)


class BlogTests(ApiTestBase):
    def setUp(self):
        super().setUp()
        self.blogs = []
        for i in range(4):
            self.blogs.append(Blog.objects.create(title='Blog %d' % i, slug='blog-%d' % i, content='<p>x</p>', author=self.admin))

    def test_blog(self):
        res = self.client.get('/api/blogs/').json()
        self.assertEqual(res['count'], 4)
        self.assertEqual(len(res['results']), 3)
        self.assertEqual(res['results'][0]['slug'], 'blog-3')          # mới nhất đứng đầu
        self.assertEqual(len(self.client.get('/api/blogs/?page=2').json()['results']), 1)

        res = self.client.get('/api/blogs/blog-2/').json()
        self.assertEqual(res['blog']['content'], '<p>x</p>')
        self.assertEqual(res['prev']['slug'], 'blog-3')
        self.assertEqual(res['next']['slug'], 'blog-1')
        self.assertEqual(res['rating']['count'], 0)
        self.assertIsNone(res['rating']['your_rate'])
        self.assertEqual(self.client.get('/api/blogs/nope/').status_code, 404)

        # chưa đăng nhập không rate / comment được
        self.assertEqual(self.client.post('/api/blogs/blog-2/rate/', {'rate': 5}, format='json').status_code, 401)
        self.assertEqual(self.client.post('/api/blogs/blog-2/comment/', {'cmt': 'hi'}, format='json').status_code, 401)

        # rate
        self.as_user('mem1')
        for bad in ('0', '6', 'abc', '', '4.5'):
            self.assertEqual(self.client.post('/api/blogs/blog-2/rate/', {'rate': bad}, format='json').status_code, 400, bad)
        res = self.client.post('/api/blogs/blog-2/rate/', {'rate': 4}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(self.client.post('/api/blogs/blog-2/rate/', {'rate': 5}, format='json').status_code, 400)   # đã rate rồi
        self.as_user('mem2')
        self.client.post('/api/blogs/blog-2/rate/', {'rate': 5}, format='json')
        res = self.client.get('/api/blogs/blog-2/').json()['rating']
        self.assertEqual(res, {'average': 5, 'average_raw': 4.5, 'count': 2, 'your_rate': 5})    # 4.5 làm tròn lên 5 kiểu PHP

        # comment + reply lồng nhau
        res = self.client.post('/api/blogs/blog-2/comment/', {'cmt': '  Hay  '}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        c1 = res.json()['comment']
        self.assertEqual(c1['cmt'], 'Hay')
        self.assertEqual(c1['level'], 0)
        self.assertEqual(self.client.post('/api/blogs/blog-2/comment/', {'cmt': ''}, format='json').status_code, 400)
        self.as_user('mem1')
        res = self.client.post('/api/blogs/blog-2/comment/', {'cmt': 'dong y', 'parent_id': c1['id']}, format='json')
        self.assertEqual(res.status_code, 201)
        c2 = res.json()['comment']
        self.assertEqual(c2['level'], 1)
        res = self.client.post('/api/blogs/blog-2/comment/', {'cmt': 'ok', 'parent_id': c2['id']}, format='json')
        self.assertEqual(res.json()['comment']['level'], 2)
        self.assertEqual(self.client.post('/api/blogs/blog-2/comment/', {'cmt': 'x', 'parent_id': 99999}, format='json').status_code, 404)
        self.assertEqual(self.client.post('/api/blogs/blog-2/comment/', {'cmt': 'x', 'parent_id': 'abc'}, format='json').status_code, 404)
        # comment của blog khác không được làm parent
        res = self.client.post('/api/blogs/blog-1/comment/', {'cmt': 'x', 'parent_id': c1['id']}, format='json')
        self.assertEqual(res.status_code, 404)

        tree = self.client.get('/api/blogs/blog-2/').json()['comments']
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]['replies'][0]['cmt'], 'dong y')
        self.assertEqual(tree[0]['replies'][0]['replies'][0]['cmt'], 'ok')
        # your_rate khi gửi token
        self.assertEqual(self.client.get('/api/blogs/blog-2/').json()['rating']['your_rate'], 4)


class AdminTests(ApiTestBase):
    def test_admin_users(self):
        self.new_product(author=self.member, images='["products/zz.jpg"]')
        self.as_admin()
        res = self.client.get('/api/admin/users/').json()
        self.assertEqual(res['count'], 3)
        by_name = {u['username']: u for u in res['results']}
        self.assertEqual(by_name['mem1']['total_products'], 1)
        self.assertEqual(by_name['boss']['role'], 'admin')
        self.assertEqual(self.client.get('/api/admin/users/?role=admin').json()['count'], 1)
        self.assertEqual(self.client.get('/api/admin/users/?role=member').json()['count'], 2)
        self.assertEqual(self.client.get('/api/admin/users/?q=mem2').json()['count'], 1)

        # sửa member: khóa tài khoản + đổi mật khẩu
        res = self.client.put('/api/admin/users/update/%d/' % self.member.id,
                              {'email': 'new@x.com', 'is_active': '0', 'password': 'newpass1', 'phone': '0909'}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)
        self.assertEqual(self.member.email, 'new@x.com')
        self.assertEqual(self.client.put('/api/admin/users/update/%d/' % self.member.id, {'email': 'bad'}, format='json').status_code, 400)
        self.assertEqual(self.client.put('/api/admin/users/update/%d/' % self.member.id, {'password': '123'}, format='json').status_code, 400)
        self.assertEqual(self.client.put('/api/admin/users/update/%d/' % self.admin.id, {'email': 'a@x.com'}, format='json').status_code, 404)   # không sửa được admin
        # member bị khóa không đăng nhập được
        self.anonymous()
        self.assertEqual(self.client.post('/api/login/', {'username': 'mem1', 'password': 'newpass1'}, format='json').status_code, 400)
        self.as_admin()

        # tạo superuser
        res = self.client.post('/api/admin/users/register-superuser/', {'username': 'boss2', 'email': 'b2@x.com', 'password': 'abcdef', 'password2': 'abcdef'}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        boss2 = User.objects.get(username='boss2')
        self.assertTrue(boss2.is_superuser and boss2.is_staff)
        self.assertEqual(boss2.level, 2)
        self.assertEqual(self.client.post('/api/admin/users/register-superuser/', {'username': 'boss2', 'email': 'b2@x.com', 'password': 'abcdef', 'password2': 'abcdef'}, format='json').status_code, 400)

        # xóa member: xóa luôn sản phẩm; admin không xóa được
        self.assertEqual(self.client.delete('/api/admin/users/delete/%d/' % self.admin.id).status_code, 404)
        res = self.client.delete('/api/admin/users/delete/%d/' % self.member.id)
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(Product.objects.count(), 0)
        self.assertFalse(User.objects.filter(id=self.member.id).exists())

    def test_admin_products(self):
        p1 = self.new_product(title='Ao A', author=self.member)
        p2 = self.new_product(title='Quan B', author=self.member2)
        self.as_admin()
        self.assertEqual(self.client.get('/api/admin/products/').json()['count'], 2)
        self.assertEqual(self.client.get('/api/admin/products/?q=quan').json()['count'], 1)
        self.assertEqual(self.client.get('/api/admin/products/?member=mem1').json()['count'], 1)
        res = self.client.put('/api/admin/products/update/%d/' % p1.id, {'title': 'Admin sua', 'price': '9'}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        p1.refresh_from_db()
        self.assertEqual(p1.title, 'Admin sua')
        self.assertEqual(p1.author, self.member)                  # chủ sản phẩm không đổi
        self.assertEqual(self.client.put('/api/admin/products/update/%d/' % p1.id, {'title': '', 'price': '9'}, format='json').status_code, 400)
        self.assertEqual(self.client.put('/api/admin/products/update/99999/', {'title': 'x', 'price': '9'}, format='json').status_code, 404)
        self.assertEqual(self.client.delete('/api/admin/products/delete/%d/' % p2.id).status_code, 200)
        self.assertEqual(self.client.delete('/api/admin/products/delete/%d/' % p2.id).status_code, 404)
        self.assertEqual(Product.objects.count(), 1)
        # member không dùng được
        self.as_user('mem1')
        self.assertEqual(self.client.delete('/api/admin/products/delete/%d/' % p1.id).status_code, 403)

    def test_admin_history(self):
        p = self.new_product(price='10.00')
        for name in ('mem1', 'mem1', 'mem2'):
            self.as_user(name)
            self.client.post('/api/cart/add/', {'product_id': p.id, 'qty': 2}, format='json')
            self.client.post('/api/checkout/', {'name': 'Khach ' + name, 'email': name + '@x.com', 'phone': '0123456789'}, format='json')
        self.as_admin()
        res = self.client.get('/api/admin/history/').json()
        self.assertEqual(res['count'], 3)
        self.assertEqual(res['summary'], {'orders': 3, 'total': 60.0})
        self.assertEqual(res['members'][0]['user__username'], 'mem1')
        self.assertEqual(res['members'][0]['orders'], 2)
        self.assertEqual(res['members'][0]['total'], 40.0)
        self.assertEqual(self.client.get('/api/admin/history/?user=%d' % self.member2.id).json()['count'], 1)
        self.assertEqual(self.client.get('/api/admin/history/?q=khach mem2').json()['count'], 1)
        self.assertEqual(self.client.get('/api/admin/history/?user=abc').json()['count'], 3)
        # xóa user thì lịch sử vẫn còn
        self.client.delete('/api/admin/users/delete/%d/' % self.member2.id)
        res = self.client.get('/api/admin/history/').json()
        self.assertEqual(res['count'], 3)


class RootTests(ApiTestBase):
    def test_root_and_cors(self):
        res = self.client.get('/api/')
        self.assertEqual(res.status_code, 200)
        res = self.client.get('/api/products/', HTTP_ORIGIN='http://localhost:3000')
        self.assertEqual(res['Access-Control-Allow-Origin'], 'http://localhost:3000')
        res = self.client.options('/api/login/', HTTP_ORIGIN='http://localhost:3000',
                                  HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
                                  HTTP_ACCESS_CONTROL_REQUEST_HEADERS='authorization,content-type')
        self.assertEqual(res.status_code, 200)
        self.assertIn('authorization', res['Access-Control-Allow-Headers'])
