Applications.InvalidPermissions = function(){}
Applications.InvalidPermissions.prototype = new App();
Applications.InvalidPermissions.constructor = Applications.InvalidPermissions;

Applications.InvalidPermissions.prototype.init = function(){}

Applications.InvalidPermissions.prototype.run = function(){}
Applications.InvalidPermissions.prototype.stop = function(){}

window.application = Applications.InvalidPermissions;