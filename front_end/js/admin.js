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