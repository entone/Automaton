function timelapse(arr, dom_ele, rate, id){
    //console.log(arr.length);
    this.loaded = 0;
    this.buffer = arr.length;
    this.arr = arr;
    this.images = [];
    this.ele = document.getElementById(dom_ele);
    this.rate = rate*1000;
    this.play_interval = 0;
    this.current_image = 0;
    this.images_loaded = new jsevent();
    this.image_updated = new jsevent();
    this.playing = false;
    this.load_image();
    this.id = id ? id : '';
}

timelapse.prototype.load_image = function(){
    //console.log('loading '+this.arr[this.loaded]);
    var im = new Image();
    im.obj = this;
    im.onload = this.image_loaded;
    im.onerror = this.image_error;
    im.src = this.arr[this.loaded];
    //im.width = this.ele.offsetWidth;
    this.images.push(im);
}

timelapse.prototype.image_loaded = function(event){
    this.obj.loaded++;
    this.obj.images_loaded.fire((this.obj.loaded/this.obj.arr.length)*100);
    if((this.obj.loaded >= this.obj.buffer) && !this.obj.playing) this.obj.play();
    if(this.obj.loaded < this.obj.arr.length) this.obj.load_image();
}

timelapse.prototype.image_error = function(event){
    this.obj.images.splice(this.obj.loaded,1);
    this.obj.arr.splice(this.obj.loaded,1);
    this.obj.buffer = this.obj.arr.length;
    if((this.obj.loaded >= this.obj.buffer) && !this.obj.playing) this.obj.play();
    if(this.obj.loaded < this.obj.arr.length) this.obj.load_image();
}

timelapse.prototype.pause = function(){
    clearInterval(this.play_interval);
    this.playing = false;
    return false;
}

timelapse.prototype.play = function(){
    if(!this.playing && this.arr.length > 1){
        //console.log('playing!!!');
        this.playing = true;
        var self = this;
        this.play_interval = setInterval(function(){
            self.update_image();
        }, this.rate);
    }else if(this.arr.length == 1){
        this.update_image();
    }
    return false;
}

timelapse.prototype.update_bar = function(){
    var im_per = Math.ceil((this.current_image/(this.arr.length-1))*100);
    document.getElementById('progress_bar'+this.id).style.width = im_per+'%';
}

timelapse.prototype.goto = function(e){
    this.pause();
    var posx = 0;
    var posy = 0;
    if (!e) var e = window.event;
    if (e.pageX || e.pageY){
        posx = e.pageX;
        posy = e.pageY;
    }
    else if (e.clientX || e.clientY)    {
        posx = e.clientX + document.body.scrollLeft
            + document.documentElement.scrollLeft;
        posy = e.clientY + document.body.scrollTop
            + document.documentElement.scrollTop;
    }
    var x = 0;
    var ele = e.currentTarget;
    while(ele != null){
        x += ele.offsetLeft;
        ele = ele.offsetParent;
    }
    var pos = posx-x;
    
    this.current_image = Math.ceil(((this.arr.length-1)/this.ele.offsetWidth)*(pos-8));
    this.update_image();
}

timelapse.prototype.update_image = function(){
    //remove previous image, if it exists.
    while(this.ele.childNodes[0]){
        this.ele.removeChild(this.ele.childNodes[0]);
    }
    //console.log(this.images[this.current_image].src+" || "+this.current_image);
    this.update_bar();
    this.ele.appendChild(this.images[this.current_image]);
    this.image_updated.fire(this.images[this.current_image]);
    this.current_image = this.current_image < this.images.length-1 ? this.current_image+1 : 0;
}