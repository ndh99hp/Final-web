// static/js/search.js: trang "Tìm kiếm nâng cao" - lọc sản phẩm bằng AJAX (không load lại trang)
// Luồng: người dùng chọn điều kiện -> JS gửi ngầm lên Python (view search_advanced_ajax)
//        -> Python lọc database, trả về HTML danh sách sản phẩm -> JS thay vào khung #search-results

var searchTimer = null;     // hẹn giờ cho ô gõ tên (gõ xong 0,3 giây mới tìm, đỡ gửi quá nhiều lần)
var searchRequest = null;   // yêu cầu AJAX đang chạy

// Lấy kết quả. page = số trang cần xem (không truyền thì là trang 1)
function loadResults(page) {
    var form = $('#search-form');
    var data = form.serialize();            // ví dụ: name=ao&price=10-50&category=1&brand=&status=
    if (page) {
        data += '&page=' + page;
    }
    $('#search-results').css('opacity', 0.5);
    if (searchRequest) {
        searchRequest.abort();              // người dùng đổi điều kiện liên tục thì bỏ yêu cầu cũ
    }
    searchRequest = $.get(form.data('url'), data, function (res) {
        $('#search-results').html(res.html).css('opacity', 1);
    }, 'json').fail(function (xhr, status) {
        if (status !== 'abort') {
            $('#search-results').css('opacity', 1);
            showToast('Có lỗi xảy ra, vui lòng thử lại', 'danger');   // showToast nằm trong cart.js
        }
    });
}

// Bấm nút Search
$('#search-form').on('submit', function (e) {
    e.preventDefault();
    loadResults();
});

// Chọn giá / danh mục / hãng / trạng thái là lọc ngay
$('#search-form select').on('change', function () {
    loadResults();
});

// Gõ tên (sự kiện 'input' cũng bắt cả dán chữ, bàn phím điện thoại): dừng gõ 0,3 giây thì lọc
$('#search-form input[name=name]').on('input', function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadResults, 300);
});

// Nút Xóa lọc: đưa form về ban đầu rồi lấy lại tất cả sản phẩm
$('#search-reset').on('click', function (e) {
    e.preventDefault();
    $('#search-form')[0].reset();
    loadResults();
});

// Bấm số trang (các link nằm trong phần kết quả được nạp bằng AJAX nên phải dùng $(document).on)
$(document).on('click', '.search-page', function (e) {
    e.preventDefault();
    loadResults($(this).data('page'));
    $('html, body').animate({ scrollTop: $('#search-form').offset().top - 20 }, 200);
});
