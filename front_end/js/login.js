function log_in(){
    var user = {
        name:"",
        password:""
    };
    user.name = $("#name").val();
    user.password = $("#password").val();
    $.post("/login",user,function(data){
        if(data == 0){
            window.location.href = "./admin.html"
        }
        else if(data == 1){
            $("#name_wrong").html("Username is wrong!");
        }
        else if(data == 2){
            $("#password_wrong").html("Password is wrong!");
        }
        else{
            $("#name_wrong").html("Username is wrong!");
            $("#password_wrong").html("Password is wrong!");
        }
    })
}
function cancle(){
    $("#name").val("");
    $("#password").val("");
    $("#name_wrong").html("");
    $("#password_wrong").html("");
}
function input_name_change(){
    $("#name_wrong").html("");
}
function input_password_change(){
    $("#password_wrong").html("");
}