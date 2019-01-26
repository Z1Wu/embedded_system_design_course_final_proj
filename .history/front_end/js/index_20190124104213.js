$(document).ready(function(){
    mytime();
});

function mytime() {
    var my_date = new Date(Date());
    var local_time = my_date.toLocaleTimeString();
    var local_date = my_date.toLocaleDateString();
    $("#time_and_msg").text("Current Time: " + local_date + " " + local_time);
    $("#time_and_msg").css("color","black")
}

var int_id = setInterval(function () {
    mytime()
}, 1000);

let re = new RegExp('^[0-9]{8}$');

function sendInputPassword() {
    let val = $("#input-password").val();
    //console.log(re.test(val))
    if (re.test(val)) {
        $.post("/open-door",val,function(data){
            if(data){
                $("#time_and_msg").text("Password is True, Lock open!")
                $("#time_and_msg").css("color","#23d160")
            }
            else{
                $("#time_and_msg").text("Password is wrong!")
                $("#time_and_msg").css("color","#ff3860")
            }
        });
    } else {
        $("#time_and_msg").text("Invalid input, password should only contain 8 number!!")
        $("#time_and_msg").css("color","#ff3860")
    }
    $("#input-password").val("")
    clearInterval(int_id);
    setTimeout(function(){int_id = setInterval(function () {
        mytime()
    }, 1000);}, 5000);
}