if(jsevent == null){
    var jsevent = function(){
        this.events = [];
    }
    
    jsevent.prototype.add = function(obj, method){
        this.events.push([obj, method]);
        return true;
    }
    
    jsevent.prototype.fire = function(args){
        if(this.events.length > 0){
            for(var i = 0; i < this.events.length; i++){
                var obj = this.events[i][0];
                var method = obj[this.events[i][1]];
                args = args.length ? args : [args];
                method.apply(obj, args)
            }
            return true;
        }else{
            return false;
        }
        return true;
    }
    
    jsevent.prototype.clear = function(){
        this.events = [];
        return true;
    }

}