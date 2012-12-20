Applications.Signin = function(){}

var EMPTY = ["", " ", null];

Applications.Signin.prototype.init = function(){
	$("#signin_form").submit(function(){
		var res = $(this).serializeArray();
		obj = {}
		for(var i in res){
			var k = res[i];
			obj[k.name] = k.value;
		}
		console.log(obj);
		empty_field = false;
		for(k in obj){
			if(EMPTY.indexOf(obj[k]) != -1){
				empty_field = true;				
			}
		}
		if(empty_field){
			alert("All fields are required");
		}
		$.post("/auth", JSON.stringify(obj), function(res){
			console.log(res);
			if(res.success){
				window.location = "/dashboard";
			}
		}, "json");
		return false;
	});
}

Applications.Signin.prototype.run = function(){}
Applications.Signin.prototype.stop = function(){}

window.application = Applications.Signin;