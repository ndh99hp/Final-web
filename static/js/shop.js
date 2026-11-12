// static/js/shop.js: thanh kéo giá màu vàng ở trang /shop/ - lọc sản phẩm bằng AJAX (không load lại trang)
// Luồng: kéo thanh -> thả chuột -> JS lấy khoảng giá + các điều kiện đang lọc trong form #price-form
//        -> gửi AJAX tới Python (view product_list_ajax) -> Python lọc database, trả về HTML danh sách sản phẩm
//        -> JS thay vào khung #shop-results bên phải

// Đang kéo: chỉ cập nhật 2 con số $ thấp - $ cao cho người dùng thấy
$('#sl2').on('slide', function (ev) {
    $('#price-low').text(ev.value[0]);
    $('#price-high').text(ev.value[1]);
});

// Thả chuột: ghi khoảng giá vào ô input (dạng "thấp,cao") rồi gửi AJAX
$('#sl2').on('slideStop', function (ev) {
    $(this).val(ev.value[0] + ',' + ev.value[1]);
    $('#price-low').text(ev.value[0]);
    $('#price-high').text(ev.value[1]);
    loadShop();
});

function loadShop() {
    var form = $('#price-form');
    $('#shop-results').css('opacity', 0.5);
    // form.serialize() = q=...&category=...&brand=...&sort=...&price=10,300
    $.get(form.data('url'), form.serialize(), function (res) {
        $('#shop-results').html(res.html).css('opacity', 1);
        // đổi link trên thanh địa chỉ cho khớp (không load lại trang), để F5 hoặc gửi link vẫn giữ khoảng giá
        history.replaceState(null, '', res.url);
    }, 'json').fail(function () {
        $('#shop-results').css('opacity', 1);
        showToast('Có lỗi xảy ra, vui lòng thử lại', 'danger');   // showToast nằm trong cart.js
    });
}
