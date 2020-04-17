function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {

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


	$("#search-form").submit(function(e){
		e.preventDefault();
        if(!$("#start_date").val() || !$("#end_date").val()){
            $("#notice").html("统计必须输入起止时间！");
            $("#notice").show();
            return;
        };
        sd = new Date($("#start_date").val().replace(/-/,"/"));
        ed = new Date($("#end_date").val().replace(/-/,"/"));
        days = Math.floor((ed - sd) / (24 * 3600 * 1000));
        if(days > 31){
            $("#notice").html("时间间隔不能超过1个月！");
            $("#notice").show();
            return;
        }
        $("#notice").hide();
        $("#export-form").hide();
        $("#download").hide();
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
                            searching: false, paging: false, info: false
                        });
                    }
                    var query = resp.query
                    $( "#export-form" ).html(
                        $( "#qhTemplate" ).render( query )
                    );
                    $("#export-form").show();
                }
                else {
                    alert(resp.errmsg);
                }
            }
        });
	})

    $("#export-form").submit(function(e){
        e.preventDefault();
        $("#prompt").show();
        $("#download").hide();
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
                $("#prompt").hide();
                if (resp.errno == "0") {
                    var filename = resp.data;
                    $( "#download" ).html(
                        $( "#dTemplate" ).render( filename )
                    );
                    $("#download").show();
                }
                else {
                    alert(resp.errmsg);
                }
            }
        });
    })
})