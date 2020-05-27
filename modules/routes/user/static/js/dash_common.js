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
