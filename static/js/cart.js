// static/js/cart.js: xử lý giỏ hàng bằng AJAX (gửi ngầm lên Python, không load lại trang)
// - Bấm nút "Thêm vào giỏ" (class btn-add-cart): lấy id sản phẩm, gửi lên server, cập nhật số trên menu giỏ hàng
// - Trang giỏ hàng: nút + / - / x

// Hiện thông báo nhỏ ở góc trên bên phải, tự mất sau 2 giây
function showToast(text, type) {
    var box = $('<div class="alert alert-' + type + '"></div>').text(text).css({
        position: 'fixed', top: '20px', right: '20px', 'z-index': 9999, 'min-width': '250px'
    });
    $('body').append(box);
    setTimeout(function () { box.fadeOut(300, function () { box.remove(); }); }, 2000);
}

// Gửi AJAX (POST) kèm csrf token (Django bắt buộc có token khi gửi POST)
function postAjax(url, data, onSuccess) {
    data.csrfmiddlewaretoken = $('body').data('csrf');
    $.post(url, data, onSuccess, 'json').fail(function (xhr) {
        var msg = 'Có lỗi xảy ra, vui lòng thử lại';
        if (xhr.responseJSON && xhr.responseJSON.message) {
            msg = xhr.responseJSON.message;
        }
        showToast(msg, 'danger');
    });
}

// ----- Thêm vào giỏ -----
// $(document).on('click', '.btn-add-cart', ...) = bắt click của mọi nút có class btn-add-cart trong trang
$(document).on('click', '.btn-add-cart', function (e) {
    e.preventDefault();
    var productId = $(this).data('id');
    // ở trang chi tiết có ô nhập số lượng (#qty), các trang khác thì mặc định 1
    var qty = $('#qty').length ? $('#qty').val() : 1;

    postAjax($('body').data('add-cart-url'), { product_id: productId, qty: qty }, function (res) {
        $('#cart-counter').text(res.cart_count);     // cập nhật số trên menu "Giỏ hàng (n)"
        showToast(res.message, 'success');
    });
});

// Đổi số thành chuỗi tiền giống cách Django hiện (web đang để tiếng Việt nên dùng dấu phẩy: $505,00)
function money(number) {
    return '$' + number.toFixed(2).replace('.', ',');
}

// ----- Trang giỏ hàng: + / - / xóa -----
function updateCart(row, action) {
    var url = $('#cart-table').data('update-url');
    postAjax(url, { id: row.data('id'), action: action }, function (res) {
        if (res.status !== 'success') {
            return;
        }
        if (action === 'delete') {
            row.remove();
            if ($('#cart-table tbody tr[data-id]').length === 0) {
                $('#empty-row').show();              // xóa hết thì hiện dòng "giỏ hàng trống"
            }
        } else {
            row.find('.cart_quantity_input').val(res.new_qty);
            row.find('.cart_total_price').text(money(res.new_total));
        }
        $('#grand-total').text(money(res.grand_total));
        $('#cart-counter').text(res.cart_count);
    });
}

$(document).on('click', '.cart_quantity_up', function () {
    updateCart($(this).closest('tr'), 'up');
});
$(document).on('click', '.cart_quantity_down', function () {
    updateCart($(this).closest('tr'), 'down');
});
$(document).on('click', '.cart_quantity_delete', function () {
    updateCart($(this).closest('tr'), 'delete');
});
