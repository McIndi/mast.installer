var Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/[^A-Za-z0-9\+\/\=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/\r\n/g,"\n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}

var xor = {
    "encode": function(string, key){
        return Base64.encode(this._xor(string, key));
    },

    "decode": function(string, key){
        string = Base64.decode(string);
        return this._xor(string, key);
    },

    "_xor": function(string, key){
        var output = "";

        for(var i=0; i<string.length; i++){
            var c = string.charCodeAt(i);
            var k = key.charCodeAt(i%key.length);

            output += String.fromCharCode(c ^ k);
        }

        return output;
    }
}

var getCookie = function(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) != -1) return c.substring(name.length,c.length);
    }
    return "";
}

var applianceTemplate = function(hostname){
    str = '<span class="bordered" id="<%hostname%>"><input type="checkbox" name="<%hostname%>" checked="checked" /><b><%hostname%></b> <span class="remove" id="remove-<%hostname%>">X</span></span>'
    return str.replace(/<%hostname%>/g, hostname)
};

var DataPower = function(hostname, username, password){
    /* This is an object constructor which produces an object
     * containing the hostname and credentials of a DataPower
     * appliance. We keep only these values because they are
     * all you need to instanciate a DataPower object on the
     * backend using the DataPower library by McIndi Solutions
     */
    this.hostname = hostname;
    this.credentials = username+':'+password;
};

var Environment = function(){
    /* This is an object constructor which produces an object
     * meant to hold references to DataPower appliances. Currently
     * the only data kept for each appliance is the hostname and
     * the credentials. This is the data needed to instanciate
     * a DataPower object on the backend using the DataPower class
     * from McIndi Solutions LLC.
     */

    self = this;
    self.appliances = [];

    self.addAppliance = function(host, user, pass, no_check_hostname){
        if (/\s/g.test(host)){
            alert("Hostname/Environment names cannot contain whitespace");
            return
        }
        $.getJSON('/environments/'+host, function(data){
            $.each(data.appliances, function(index, appliance){
                self.appliances.push(new DataPower(appliance, user, pass));
            });
            $.publish('modifyAppliances', self.appliances);
        });
    };

    self.removeAppliance = function(hostname){
        var newAppliances = []
        $.each(self.appliances, function(index, appliance){
            if(appliance.hostname != hostname){
                newAppliances.push(appliance);
            }
        });
        self.appliances = newAppliances;
        $.publish('modifyAppliances', self.appliances);
    };
}

var environment = new Environment();

$.subscribe('modifyAppliances', function(event, appliances){
    /*"""
      This is subscribed to the modifyAppliances topic. This means
      that when an appliance is added or removed this function is called.
      modifyAppliances is published to from within the Environment.addAppliance
      and Environment.removeAppliance methods meaning that when an appliance is
      added or removed this function will be called and this function will
      update the area which lists the current appliances.
      """*/
    htm = []
    // Gather all of the hostnames from the parameter passed into an array
    // and apply the template to get valid html
    $.each(appliances, function(index, appliance){
        htm.push(applianceTemplate(appliance.hostname))
        credentials = xor.encode(appliance.credentials, xor.encode(getCookie("9x4h/mmek/j.ahba.ckhafn"), "_"))
        no_check_hostname = $( "#addApplianceForm" ).find("input[name='global_no_check_hostname']").prop('checked');
        data = {"credentials": credentials, "check_hostname": !no_check_hostname};
        $.get("/test/connectivity/"+appliance.hostname, data, function( data ){
            var id = "#" + appliance.hostname.replace( /(:|\.|\[|\])/g, "\\$1" );
            if (data.soma === false){
                $( id ).addClass( "red" );
            } else {
                if (data.ssh === false){
                    $( id ).addClass( "yellow" );
                }
            }
        }).fail(function(){
            var id = "#" + appliance.hostname.replace( /(:|\.|\[|\])/g, "\\$1" );
            $( id ).addClass( "red" );
        });
    });
    // Put the list of hostnames in #currentAppliances along with the label
    // Current Appliances: in italics
    $("#currentAppliances").html('<i>Current Appliances:</i> '+htm.join(' '));
});

$( document ).ready(function(){
    $("#tabs").tabs();

    $("#addApplianceForm").on("keypress", 'input[name="password"]', function(e) {
        if (e.keyCode == 13) {
            $("#addAppliance").trigger("click");
        }
    });

    $("#addAppliance").on("click", function(event){
        // This is used to handle adding an appliance to environment.
        // #addAppliance is a button near the top of the page
        // which is part of a form. Here we grab all of the values from the
        // form and pass them to environment.addAppliance()
        hostname = $(event.target).parent().find("input[name='hostname']").val();
        username = $(event.target).parent().find("input[name='username']").val();
        password = $(event.target).parent().find("input[name='password']").val();
        environment.addAppliance(hostname, username, password);
    });

    $("#currentAppliances").on("click", ".remove", function(event){
        hostname = $(event.target).parent().attr("id");
        environment.removeAppliance(hostname);
    });

    $("#main").on("click", ".multiTextButton", function(event){
        target = $(event.target);
        // parent = target.parent();
        input = target.parent().find(".multiTextTextbox");
        value = input.val();
        if (value.length == 0 ){
            return
        }
        input.val("");
        currentChoices = target.parent().find(".multiTextCurrent");
        choices = currentChoices.html().replace("<i>Current selection: </i>", "").split(" ");
        choices.push("<span class='multiTextSelection bordered'>"+value+"<span class='multiTextSelectionCancel'> X </span></span>");
        currentChoices.html("<i>Current selection: </i>"+choices.join(" "));
    });

    $("#main").on("click", ".multiTextSelectionCancel", function(event){
        target = $(event.target);
        target.parent().remove();
    });

    $("#main").on("change", ".multiSelect", function(event){
        target = $(event.target);
        value = target.val();
        if (value.length == 0 ){
            return
        }
        // parent = target.parent();
        currentChoices = target.parent().find(".multiSelectCurrent");
        choices = currentChoices.html().replace("<i>Current selection: </i>", "").split(" ");
        choices.push("<span class='multiSelectSelection bordered'>"+value+"<span class='multiSelectSelectionCancel'> X </span></span>");
        currentChoices.html("<i>Current selection: </i>"+choices.join(" "));
    });

    $("#main").on("click", ".multiSelectSelectionCancel", function(event){
        target = $(event.target);
        target.parent().remove();
    });

    $( "#main" ).on( "click", ".toggle", function( event ){
        event.preventDefault();
        target = $( event.target );
        id = "#" + target.attr( "name" );
        $( id ).toggle();
        if ( target.text() == "Show" ){
            target.text( "Hide" );
        } else {
            target.text( "Show" );
        }
    } );

    $(document).bind("ajaxStart", function(){
        $("#hiddenLoadingIMG").show();
        $("#main").css({opacity: 0.5});
    }).bind("ajaxStop", function(){
        $("#hiddenLoadingIMG").hide();
        $("#main").css({opacity: 1.0});
    });
});
