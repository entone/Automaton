Applications.Historical = function(){}
Applications.Historical.prototype = new App();
Applications.Historical.constructor = Applications.Historical;

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
        $("#graph").html("");
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
        that.draw_graph(res, ele);
    }, "json");
}

Applications.Historical.prototype.draw_graph = function(res, ele){    
    for(var sensor in res.result.data){
        var ar = res.result.data[sensor].data;
        for(var i in ar){
            ar[i][0]+=offset;
        }
    }
    this.graph = $.plot($("#graph"), res.result.data, {
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
        },
        legend:{
            backgroundColor:"#FFFFFF",
        }
    });
    this.enable_rollover();
    $('#custom_range').popover('hide');
    $(ele).button('reset');
    this.enable_download();    
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