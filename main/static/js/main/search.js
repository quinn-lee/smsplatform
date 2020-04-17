function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {

    $.get("/api/v1.0/session", function(resp){
        if ("4101" == resp.errno) {
            // 用户未登录
            location.href = "/login.html";
        } else {
        	$("#login-name").html(resp.data['name']);
        }
    });

	$.datetimepicker.setLocale('ch');
    $('.datepicker').datetimepicker({
        i18n:{
          ch:{
           months:[
            '一月','二月','三月','四月',
            '五月','六月','七月','八月',
            '九月','十月','十一月','十二月',
           ],
           dayOfWeek:[
            "日", "一", "二", "三", "四", "五", "六",
           ]
          }
         },
         timepicker:false,
         format:'Y/m/d'
    });

    $.get("/api/v1.0/msg_orgs", function (resp) {
        if (resp.errno == "0") {
            var orgs = resp.data;
            $( "#msgorg" ).html(
				$( "#orgTemplate" ).render( orgs )
			);

        } else {
            alert(resp.errmsg);
        }

    }, "json");

    $.get("/api/v1.0/msg_classes", function (resp) {
        if (resp.errno == "0") {
            var classes = resp.data;
            $( "#msgclass" ).html(
				$( "#classTemplate" ).render( classes )
			);

        } else {
            alert(resp.errmsg);
        }

    }, "json");

    $("#logout a").click(function(e){
    	$.ajax({
            url:"/api/v1.0/session",
            type:"delete",
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    location.href = "/login.html";
                }
                else {
                	location.href = "/login.html";
                }
            }
        });
    })

	$("#search-form").submit(function(e){
		e.preventDefault();
		var data = {
            start_date: $("#start_date").val(),
            end_date: $("#end_date").val(),
            msg_org: $("#msgorg").val(),
            msg_class: $("#msgclass").val(),
            msg_status: $("#msg_status").val(),
            action: 'search'
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
		$.ajax({
            url:"/api/v1.0/msg_statistics",
            type:"post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    var res = resp.data;
            		$( "#table-tr" ).html(
						$( "#trTemplate" ).render( res )
					);
                    if (typeof(resultTable) == "undefined") {
                        resultTable = $('#result-listing').DataTable({
                          "aLengthMenu": [
                            [5, 10, 15, -1],
                            [5, 10, 15, "All"]
                          ],
                          "iDisplayLength": 10,
                          "language": {
                            search: ""
                          },
                          searching: false, paging: false, info: false
                        });
                    }
                    var query = resp.query
                    $( "#export-form" ).html(
                        $( "#qhTemplate" ).render( query )
                    );
                }
                else {
                    alert(resp.errmsg);
                }
            }
        });
	})

    $("#export-form").submit(function(e){
        e.preventDefault();
        var data = {
            start_date: $("#qstart_date").val(),
            end_date: $("#qend_date").val(),
            msg_org: $("#qmsg_org").val(),
            msg_class: $("#qmsg_class").val(),
            msg_status: $("#qmsg_status").val(),
            action: 'export'
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/msg_statistics",
            type:"post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    var filename = resp.data;
                    $( "#download" ).html(
                        $( "#dTemplate" ).render( filename )
                    );
                }
                else {
                    alert(resp.errmsg);
                }
            }
        });
    })
})