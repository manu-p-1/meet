$(function () {
    let form = $("#searchForm");
    form.on("submit",function(e){
        e.preventDefault();
        $.ajax({
            url: `/util/manage_plan/?value=${$("#planSearch").val()}`,
            type: 'GET',
            success: function(data){
                console.log("printing response out");
                console.log(data);
                $("#managePlan").html(data);
            }
        });
    })


})