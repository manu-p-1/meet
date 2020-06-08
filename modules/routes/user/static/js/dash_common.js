function showConfirmModal(message, callback) {
    displayModal($("#confirmModal"), message, callback);
}

function showErrorModal(message, callback) {
    displayModal($("#errorModal"), message, callback);
}

function displayModal(modalref, message, callback) {
    modalref.find(".modal-body").html(`<p>${message}</p>`);
    modalref.unbind().modal('show');
    modalref.find(".modal-footer .btn-modal-proceed").unbind().on("click", function (e) {
        if(!(callback === null || callback === undefined)) {
            callback();
        }
    });
    // $('body').removeClass('modal-open');
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

const dmst = $("#darkModeSelector");
const dmst_txt = $("#darkModeSelectorText");
dmst.on("click", handler1);


if (window.localStorage.getItem("MEET_DARK") === "1"){
    dmst.trigger("click");
}


function handler1() {
    $(this).one("click", handler2);
    DarkReader.setFetchMethod(window.fetch);
    DarkReader.enable(readerOptions);
    dmst_txt.html("Disable Dark Mode");
    window.localStorage.setItem("MEET_DARK", "1");
}
function handler2() {
    $(this).one("click", handler1);
    DarkReader.disable();
    dmst_txt.html("Enable Dark Mode");
    window.localStorage.removeItem("MEET_DARK");
}

const currency_formatter = Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
});