function toggle(type, id, index, label, on, node, callback){
    this.type = type;
    this.id = id;
    this.index = index;
    this.label = label;
    this.node = node;
    this.on = on || false;
    this.dom = document.getElementById(this.id);
    this.dom.onclick = this.toggle;
    this.dom.children[0].innerHTML = this.label;
    this.dom.obj = this;
    this.callback = callback;
    if(this.on) this.turn_on();
}

toggle.prototype.set_state = function(state){
    if(state == true){
        this.turn_on();
    }else{
        this.turn_off();
    }
}

toggle.prototype.turn_on = function(){
    this.dom.children[1].classList.add('on');
}

toggle.prototype.turn_off = function(){
    this.dom.children[1].classList.remove('on');
}        

toggle.prototype.toggle = function(e){
    if(this.obj.on){
        this.obj.on = false;
        this.obj.turn_off(); 
    }else{
        this.obj.on = true;
        this.obj.turn_on();
    }
    this.obj.callback(this.obj);
}