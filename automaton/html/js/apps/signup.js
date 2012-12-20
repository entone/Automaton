Applications.Signup = function(){}

var EMPTY = ["", " ", null];

Applications.Signup.prototype.init = function(){
    $("#signup_form").submit(function(){
        var res = $(this).serializeArray();
        obj = {}
        for(var i in res){
            var k = res[i];
            obj[k.name] = k.value;
        }
        console.log(obj);
        if(obj.password != obj.confirm_password){
            alert("Passwords must match");
        }
        empty_field = false;
        for(k in obj){
            if(EMPTY.indexOf(obj[k]) != -1){
                empty_field = true;             
            }
        }
        if(empty_field){
            alert("All fields are required");
        }
        $.post("/create_account", JSON.stringify(obj), function(res){
            console.log(res);
        }, "json");
        return false;
    });
}

Applications.Signup.prototype.run = function(){}
Applications.Signup.prototype.stop = function(){}

window.application = Applications.Signup;