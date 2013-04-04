Applications.Calibrate = function(){}
Applications.Calibrate.prototype = new App();
Applications.Calibrate.constructor = Applications.Calibrate;

Applications.Calibrate.prototype.init = function(){    
    console.log("Calibrate");
    var that = this;
    $(".calibrate").click(function(){        
        $(this).button('loading');
        $(this).button('toggle');
        var id = $(this).attr('id');
        var node = $("#node").val();
        that.calibrate(node, id, this);
        return false;
    });    
}

Applications.Calibrate.prototype.calibrate = function(node, id, ele){
    var url = "/calibrate/node/"+node+"/"+id+"/";
    this.get_url(url, function(res){
        console.log(res);
        $(ele).button('reset');
    }, "json");
}

Applications.Calibrate.prototype.run = function(){}
Applications.Calibrate.prototype.stop = function(){}

window.application = Applications.Calibrate;