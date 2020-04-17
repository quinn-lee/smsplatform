function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function() {

    var queryData = decodeQuery();
    var startDate = queryData["start_date"];
    var endDate = queryData["end_date"];
    var orgCode = queryData["org_code"];

    $.get("/api/v1.0/session", function(resp){
        if ("4101" == resp.errno) {
            // 用户未登录
            location.href = "/login.html";
        } else {
        	$("#login-name").html(resp.data['name']);
        }
    });


    //提示信息
    $.fn.dataTable.ext.errMode = 'none';

    var lang = {
        "sProcessing": "获取数据中...",
        "sLengthMenu": "每页 _MENU_ 条",
        "sZeroRecords": "没有匹配结果",
        "sInfo": "当前显示第 _START_ 至 _END_ 条，共 _TOTAL_ 条。",
        "sInfoEmpty": "当前显示第 0 至 0 条，共 0 条",
        "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
        "sInfoPostFix": "",
        "sSearch": "搜索:",
        "sUrl": "",
        "sEmptyTable": "表中数据为空",
        "sLoadingRecords": "载入中...",
        "sInfoThousands": ",",
        "oPaginate": {
            "sFirst": "首页",
            "sPrevious": "上页",
            "sNext": "下页",
            "sLast": "末页",
            "sJump": "跳转"
        },
        "oAria": {
            "sSortAscending": ": 以升序排列此列",
            "sSortDescending": ": 以降序排列此列"
        }
    };

    //初始化表格
    table = $("#table_details")
        .on('error.dt', function (e, settings, techNote, message) {
            console.warn(message)
        }).dataTable({
            "aLengthMenu": [
                    [100, 500, 1000],
                    [100, 500, 1000] // change per page values here
                ],
            iDisplayLength: 100,
            language: lang, //提示信息
            autoWidth: false, //禁用自动调整列宽
            stripeClasses: ["odd", "even"], //为奇偶行加上样式，兼容不支持CSS伪类的场合
            processing: true, //隐藏加载提示,自行处理
            serverSide: true, //启用服务器端分页
            searching: false, //禁用原生搜索
            orderMulti: false, //启用多列排序
            order: [], //取消默认排序查询,否则复选框一列会出现小箭头
            renderer: "bootstrap", //渲染样式：Bootstrap和jquery-ui
            pagingType: "simple_numbers", //分页样式：simple,simple_numbers,full,full_numbers
            columnDefs: [{
                "targets": 'nosort', //列的样式名
                "orderable": false //包含上样式名‘nosort'的禁止排序
            }],
            ajax: function (data, callback, settings) {
                //封装请求参数
                var param = {};
                param.pageSize = data.length;//页面显示记录条数，在页面显示每页显示多少项的时候
                param.start = data.start;//开始的记录序号
                param.currentPage = (data.start / data.length) + 1;//当前页码
                param.action = 'search';
                param.org_code = orgCode;
                param.start_date = startDate;
                param.end_date = endDate;
                //console.log(param);
                //ajax请求数据
                $.ajax({
                    type: "GET",
                    url: "/api/v1.0/org_details",
                    cache: false, //禁用缓存
                    data: param, //传入组装的参数
                    dataType: "json",
                    success: function (result) {
                        var returnData = {};
                        returnData.draw = data.startRow;//这里直接自行返回了draw计数器,应该由后台返回
                        returnData.recordsTotal = result.totalRows;//返回数据全部记录
                        returnData.recordsFiltered = result.totalRows;//后台不实现过滤功能，每次查询均视作全部结果
                        returnData.data = result.data ;//返回的数据列表
                        //此时的数据需确保正确无误，异常判断应在执行此回调前自行处理完毕
                        callback(returnData);
                    }
                });
            },
            "columns": [   
                //跟你要显示的字段是一一对应的。我这里只显示八列
                {'data': 'name',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,6) + "</a>";
                        }
                    }
                },
                {'data': 'id_no',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,6)+ "**"+ data.substr(-4,4) + "</a>";
                        }
                    }
                },
                {'data': 'mobile',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,3)+ "**"+ data.substr(-3,3) + "</a>";
                        }
                    }
                },
                {'data': 'mtq_stime',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,8) + "</a>";
                        }
                    }
                },
                {'data': 'mtq_msg',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,10) + "</a>";
                        }
                    }
                },
                {'data': 'send_class',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,10) + "</a>";
                        }
                    }
                },
                {'data': 'send_name',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,6) + "</a>";
                        }
                    }
                },
                {'data': 'msgcontent',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,6) + "</a>";
                        }
                    }
                },
                {'data': 'send_date',
                    render: function (data, type, full) {
                        if(data != null){
                            return "<a data-toggle='tooltip' title='" + data + "'> "+ data.substr(0,8) + "</a>";
                        }
                    }
                },
            ],
            "fnRowCallback": function (nRow, aData, iDisplayIndex, iDisplayIndexFull)            {                    //列样式处理
            }
        })
        .api();


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


    $("#export-form").submit(function(e){
        e.preventDefault();
        var data = {
            action: 'export'
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/org_details",
            type:"get",
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