function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {

    $.get("/api/v1.0/balance", function (resp) {
        if (resp.errno == "0") {
            var data = resp.data;
            $( "#result-show" ).html(
				$( "#rTemplate" ).render( data )
			);

        } else {
            alert(resp.errmsg);
        }

    }, "json");

})