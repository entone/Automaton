if(typeof console === "undefined") {
    console = {
        log: function() {},
        debug: function() {}
    };
}

function API(){
    this.URL = "${url}";
}

API.prototype.fetch = function(url, data, async){
    async = async ? async : false;
    var x=window.XMLHttpRequest?new XMLHttpRequest():new ActiveXObject('Microsoft.XMLHTTP');
    var that = this;
    x.onreadystatechange=function(){
        if(x.readyState==4 && x.status==200){
            try{
                var res = JSON.parse(x.responseText);                            
                if(that.callback) that.callback(res);
            }catch(e){
                console.log(e);
            }
        }
    };
    if(data){
        try{
            x.open('POST', url, async);
            x.setRequestHeader('Content-type','application/json');
            x.withCredentials = "true";
            data = JSON.stringify(data);
            x.send(data);
        }catch(e){
            console.log(e);
        }
    }else{
        x.open('GET', url, async);
        x.send(null);
    }
}

API.prototype.send = function(data, endpoint, callback){
    var url = this.URL+endpoint;
    this.callback = callback;
    this.fetch(url, data, true);
}

Share.prototype = new API();
Share.prototype.constructor = Share;

function Share(url, channel, topic, callback){
    this.send({url:url, channel:channel, topic:topic}, '/share/', callback);
}

Donate.prototype = new API();
Donate.prototype.constructor = Donate;

function Donate(amount, url, callback){
    this.send({amount:amount, url:url}, '/donate/', callback);
}

RSVP.prototype = new API();
RSVP.prototype.constructor = RSVP;

function RSVP(event, url, callback){
    this.send({event:event, url:url}, '/rsvp/', callback);
}

Signup.prototype = new API();
Signup.prototype.constructor = Signup;

function Signup(email, zip, url, callback){
    this.send({email:email, zip:zip, url:url}, '/signup/', callback);
}

Progress.prototype = new API();
Progress.prototype.constructor = Progress;

function Progress(marker, url, callback){
    this.send({marker:marker, url:url}, '/progress/', callback);
}

Target.prototype = new API();
Target.prototype.constructor = Target;

function Target(fb_id, campaign_id, url, channel, topic, callback){
    this.send({fb_id:fb_id, campaign_id:campaign_id, url:url, channel:channel, topic:topic}, '/target/', callback);
}

Like.prototype = new API();
Like.prototype.constructor = Like;

function Like(channel, url, callback){
    this.send({channel:channel, url:url}, '/like/', callback);
}

Aggregate.prototype = new API();
Aggregate.prototype.constructor = Aggregate;

function Aggregate(user, callback){
    this.send({user:user}, '/aggregate/', callback);
}

Shared.prototype = new API();
Shared.prototype.constructor = Shared;

function Shared(shares, callback){
    this.send({shares:shares}, '/shared/', callback);
}