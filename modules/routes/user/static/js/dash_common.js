function showConfirmModal(message, callback) {
    displayModal($("#confirmModal"), message, callback);
}

function showErrorModal(message, callback) {
    displayModal($("#errorModal"), message, callback);
}

function displayModal(modalref, message, callback) {
    modalref.find(".modal-body").html(`<p>${message}</p>`);
    modalref.modal('show');
    modalref.find(".modal-footer .btn-modal-proceed").on("click", function (e) {
        if(!(callback === null || callback === undefined)) {
            callback();
        }
    });
    $('body').removeClass('modal-open');
}

$('[data-toggle="tooltip"]').tooltip();


/*
 * Dark Reader
 *
 */
const readerOptions = {
    brightness: 100,
    contrast: 90,
    sepia: 10
};

$("#darkModeSelector").on("click", handler1);
const dmst = $("#darkModeSelectorText");

function handler1() {
    $(this).one("click", handler2);
    DarkReader.enable(readerOptions);
    dmst.html("Disable Dark Mode");
}
function handler2() {
    $(this).one("click", handler1);
    DarkReader.disable();
    dmst.html("Enable Dark Mode");
}

const currency_formatter = Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
});