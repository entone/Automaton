Applications.ManualReadings = function(){
}

Applications.ManualReadings.prototype = new App();
Applications.ManualReadings.constructor = Applications.ManualReadings;

Applications.ManualReadings.prototype.init = function(){    
    $("#type").change(function(){
        var val = $(this).val();
        if(val == 'marker'){
            $('#marker').removeClass('hide');
            $('#value').addClass('hide');
        }else{
            $('#marker').addClass('hide');
            $('#value').removeClass('hide');
        }
    });
    var that = this;
    $("#save").click(function(){
        var obj = {};
        obj.node = $("#node").val();        
        obj.sensor = $("#type").val();
        var val = 'value'
        if(obj.sensor == 'marker'){
            val = 'marker';
        }
        obj.value = $("#"+val).val();        
        console.log(obj);
        that.post("/manual_readings/save/", JSON.stringify(obj), function(res){
            if(res.id){
                $(".alert-success").removeClass('hide');
            }
        })
        return false;
    })
}

Applications.ManualReadings.prototype.run = function(){}
Applications.ManualReadings.prototype.stop = function(){}

window.application = Applications.ManualReadings;