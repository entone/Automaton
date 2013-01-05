Applications.Settings = function(){
    this.prefs = {};
    this.last = {};
    this.data = {};
    this.h_data = {};
}

Applications.Settings.prototype = new App();
Applications.Settings.constructor = Applications.Dashboard;

Applications.Settings.prototype.init = function(){
    $( "#start" ).slider({
        range: true,
        min: 0,
        max: 1440,
        values: [ 75, 300 ],
        slide: function(event, ui) {
            $( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
        }
    });
    $( "#amount" ).val( "$" + $( "#start" ).slider( "values", 0 ) +
        " - $" + $( "#start" ).slider( "values", 1 ) );
    });
}

Applications.Settings.prototype.run = function(){}
Applications.Settings.prototype.stop = function(){}

window.application = Applications.Settings;