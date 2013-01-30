var colors = ["#80DE03", "#C53437", "#6FDDFC", "#1D8480", "#E25618"];
var decorators = {ph: "", temperature:"&deg;C",humidity:"%",light:"%", etape:"cm", ec:"ppm", dissolved_oxygen:"ppm"}
var offset = -(new Date().getTimezoneOffset()*60*1000);   
var last_x = new Date().getTime()+offset;
var daynode_height = 10;

function zeroFill(number, width){
    width -= number.toString().length;
    if (width > 0){
        return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
    }
    return number + ""; // always return a string
}

function rpc_on_off(obj){
    console.log("Setting:");
    obj = {node:obj.node, index:obj.index, state:obj.on};
    console.log(obj);
    $.post("//"+url+"/rpc/", JSON.stringify(obj), function(res){
        console.log(eval("("+res+")"));
    });
}

function format_time(minutes){
    var hours = String('00'+parseInt(minutes/60)).slice(-2);
    var min = String('00'+parseInt(minutes%60)).slice(-2);
    return hours+":"+min;
}

function showTooltip(x, y, contents){
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 5,
        border: '1px solid #fdd',
        padding: '2px',
        'background-color': '#fee',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

window.onload = function(){    
    this.app = new this.application();
    this.app.init();
};

window.onblur = function(){
    this.app.stop();
};

window.onfocus = function(){
    this.app.run();
};

function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}

var App = function(){

}

App.prototype.handle_response = function(res, cb){
    switch(res.status){
        case "redirect":
            window.location = res.location;
            break;
        default:
            cb(res);
    }
}

App.prototype.post = function(url, data, cb){
    var that = this;
    $.post(url, data, function(res){
        that.handle_response(res, cb);
    }, "json");
}

App.prototype.get_url = function(url, cb){
    var that = this;
    $.get(url, function(res){
        that.handle_response(res, cb);
    }, "json");
}