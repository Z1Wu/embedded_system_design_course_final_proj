$(document).ready(function(){
    mytime();
});
function mytime() {
    var my_date = new Date(Date());
    var local_time = my_date.toLocaleTimeString();
    var local_date = my_date.toLocaleDateString();
    $("#time").text(local_date + " " + local_time);
}
var int_id = setInterval(function () {
    mytime()
}, 1000);
function go_home(){
    window.location.replace("./index.html")
}

function info_change_click(){
    $("#overview").removeClass("is-active");
    $("#change_login_info").addClass("is-active");
}
function submit_info(){
    var user = {
        name:"",
        password:""
    };
    user.name = $("#name").val();
    user.password = $("#password").val();
    $.post("/change_info",user,function(data){
        if(data){
            $("#change_info").css("display","none");
            alert("Change Success!")
        }
        else{
            $("#change_info").css("display","none");
            alert("Change Fail!")
        }
    })
}
function cancle_change_info(){
    $("#name").val("");
    $("#password").val("");
    $("#change_login_info").removeClass("is-active");
    $("#overview").addClass("is-active");
}

function pass_change_click(){
    $("#overview").removeClass("is-active");
    $("#change_pass").addClass("is-active");
}
let re = new RegExp('^[0-9]{8}$');

function submit_new_pass(){
    var new_lock_password = $("#lock_password").val();
    if(re.test(new_lock_password)){
        $.post("/change_lock_password",new_lock_password,function(data){
            if(data){
                alert("Change Success!")
            }
            else{
                alert("Change Fail!")
            }
        })
    }
    else{
        alert("Invalid input, password should only contain 8 number!!");
    }
}
function cancle_change_pass(){
    $("#lock_password").val("");
    $("#change_pass").removeClass("is-active");
    $("#overview").addClass("is-active");
}

function get_status(){
    $("#overview").removeClass("is-active");
    $("#get_status").addClass("is-active");
    $.get("/get_lock_status",function(data,status){
        $("#status").html(data);
    })
}

function close_status(){
    $("#overview").addClass("is-active");
    $("#get_status").removeClass("is-active");
}

function get_log(){
    $("#overview").removeClass("is-active");
    $("#get_log").addClass("is-active");
    $.get("/get_log",function(data,status){
        $("#log").html(data);
    })
}

function close_log(){
    $("#overview").addClass("is-active");
    $("#get_log").removeClass("is-active");
}