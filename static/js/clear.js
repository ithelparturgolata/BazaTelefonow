$(document).ready(function(){

    $(document).on("click", "#empTable tbody .select-checkbox", function(){

        let tel = $(this).next().next().next().next().next().next().html();
        $("#phone").reset(tel);

	});
});