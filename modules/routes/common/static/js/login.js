$("#email").on("input", function (e) {
    if ($(this).val().length) {
        $(this).addClass("valid");
    } else {
        $(this).removeClass("valid");
    }
});

$("#password").on("input", function (e) {
    if ($(this).val().length) {
        $(this).addClass("valid");
    } else {
        $(this).removeClass("valid");
    }
});

$("#loginForm").on("submit", function () {
    replaceBtn("#loginBtn");
});

$("#loginBtn").on("click", function () {
    $("loginForm").submit();
});

$(function () {
    setInterval(function () {
        let r = $("#email");
        if (r.val().length !== 0) {
            r.focus();
        }
    }, 2000);
});