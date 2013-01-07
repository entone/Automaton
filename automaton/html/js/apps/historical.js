Applications.Historical = function(){}
Applications.Historical.prototype = new App();
Applications.Historical.constructor = Applications.Historical;

var marker = null;

Applications.Historical.prototype.init = function(){    
    var content = $('#custom_content').html()
    $('#custom_range').popover({html:true,placement:'bottom', content:content});
    var that = this;
    $('#custom_range').click(function(){
        setTimeout(function(){
            $('.date').data('date',today);
            $('.date').datepicker();
            $("#custom").click(function(ele){
                $(this).button('loading');
                $(this).button('toggle');
                var id = $(this).attr('id');
                var node = $("#node").val();
                that.fetch_data(node, id, this);
                return false;
            });
        }, 500);
    });    
    this.bind_dl_buttons(); 
    $("#hour").click();    
}

Applications.Historical.prototype.bind_dl_buttons = function(){
    var that = this;
    $(".get-csv").click(function(){        
        try{
            that.timelapse.pause();            
        }catch(e){}
        delete that.timelapse;
        delete that.graph_data;
        $("#graph").html("");
        $("#timelapse").html("");        
        $("#downloader").hide();        
        $(this).button('loading');
        $(this).button('toggle');
        var id = $(this).attr('id');
        var node = $("#node").val();
        that.fetch_data(node, id, this);        
        return false;
    });    
}

Applications.Historical.prototype.fetch_data = function(node, id, ele){
    var url = "/historical/data/"+node+"/"+id;
    this.current_node = node;
    this.current_id = id;
    if(id=="custom"){
        from = $("#from").val();
        to = $("#to").val();
        url+= "/"+from+"/"+to;
        this.current_from = from;
        this.current_to = to;
    }
    var that = this;
    this.get_url(url, function(res){
        that.draw_timelapse(res, ele);
    }, "json");
}

Applications.Historical.prototype.draw_timelapse = function(res, ele){
    try{
        this.timelapse.pause();    
        delete this.timelapse;
    }catch(e){}    
    var template = $('#timelapse_template').html();
    var obj = {object:"window.app.timelapse"}
    if(res.result.images.length){
        obj.images = true;
    }
    var output = Mustache.to_html(template, obj);
    $('#timelapse').html(output);
    rate = (200-res.result.images.length)/(500);
    var images = [];
    for(var i in res.result.images){
        images.push(res.result.images[i].file);
    }
    this.images = res.result.images;
    this.timelapse = new timelapse(images, 'images1', rate, '');
    this.timelapse.image_updated.add(this, 'update_graph');
    this.timelapse.image_updated.add(this, 'update_time_display');
    var that = this;
    var a = {};
    a.update_percent = function(percent){
        $('#loading_bar').css('width',percent+'%');
    }   
    $('#progress_holder').click(function(e){
        that.timelapse.goto(e)
    });
    this.timelapse.images_loaded.add(a, 'update_percent');
    this.draw_graph(res, ele);
}

Applications.Historical.prototype.update_graph = function(image){
    for(var i in this.images){
        if(this.images[i].file == image.src){
            marker = this.images[i].mod+offset;
            this.draw_graph();
            break;
        }
    }
}

Applications.Historical.prototype.update_time_display = function(image){
    for(var i in this.images){
        if(this.images[i].file == image.src){
            marker = this.images[i].mod;
            var d = new Date(marker);
            console.log(d.toString());
            $("#time_display").html(d.toString());
            break;
        }
    }
}

Applications.Historical.prototype.draw_graph = function(res, ele){    
    if(!this.graph_data){
        for(var sensor in res.result.data){
            var ar = res.result.data[sensor].data;
            for(var i in ar){
                ar[i][0]+=offset;
            }
        }
        this.graph_data = res.result.data;
    }
    this.graph = $.plot($("#graph"), this.graph_data, {
        series: { 
            lines: { 
                show: true, 
                fill: false
            },
            points:{
                show:true,
                fill:true,
            }
        },
        yaxis: { 
            min: 0,
            max: 100,
        },
        xaxis: {
            mode: "time",
            timeformat:"%m/%d %H:%M",
            minTickSize: [10, "minute"],
        },
        grid:{
            color: "ffffff",
            backgroundColor: "eeeeee",
            borderWidth: 3,
            borderColor: "dddddd",
            hoverable: true,
            markings: this.markings,
        },
        legend:{
            backgroundColor:"#FFFFFF",
            position: "nw",
        },        
    });
    if(res){
        this.enable_rollover();
        $('#custom_range').popover('hide');    
        $(ele).button('reset');
        this.enable_download();    
    }
}

Applications.Historical.prototype.markings = function(axes){
    marker = marker ? marker : axes.xaxis.min;
    var wid = ((axes.xaxis.max-axes.xaxis.min)/100)*.2;
    return [{xaxis:{from:marker,to:marker+wid}, color:"#333333"}];
}

Applications.Historical.prototype.enable_download = function(){
    $("#downloader").show();
    var that = this;
    $("#download-button").click(function(ev){
        that.fetch_csv(that.current_node, that.current_id);
        return false;
    })
}

Applications.Historical.prototype.enable_rollover = function(){
    var previousPoint = null;
    $("#graph").bind("plothover", function (event, pos, item) {
        if (item) {
            if (previousPoint != item.dataIndex) {
                previousPoint = item.dataIndex;
                
                $("#tooltip").remove();
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);
                
                showTooltip(item.pageX, item.pageY, y);
            }
        }
        else {
            $("#tooltip").remove();
            previousPoint = null;            
        }
    });
}

Applications.Historical.prototype.fetch_csv = function(node, id){
    var url = "/historical/csv/"+node+"/"+id;
    if(id=="custom"){
        from = this.current_from;
        to = this.current_to;
        url+= "/"+from+"/"+to;
    }
    window.location = url;
}

Applications.Historical.prototype.run = function(){}
Applications.Historical.prototype.stop = function(){}

window.application = Applications.Historical;

window.onresize = function(){
    this.app.graph.resize();
    this.app.graph.setupGrid();
    this.app.graph.draw();

}