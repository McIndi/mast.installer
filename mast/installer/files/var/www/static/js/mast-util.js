
var addClickCallbackToButtons = function(plugin){
    $("#"+plugin).on("click", "."+plugin+"Button", function(event){
        var appliances  = [];
        var credentials = [];
        $.each(environment.appliances, function(index, appliance){
            if($("input[type='checkbox'][name='"+appliance.hostname+"']").is(":checked")){
                appliances.push(encodeURIComponent(appliance.hostname));
                credentials.push(encodeURIComponent(xor.encode(appliance.credentials, xor.encode(getCookie("9x4h/mmek/j.ahba.ckhafn"), "_"))));
            }
        });

        target = $(event.target);
        callable = target.attr("value").replace(/ /g, "_");
        data = {
            'callable': callable,
            'appliances[]': appliances,
            'credentials[]': credentials}

        var uri = plugin.split( "." )[2];
        $.get('/'+uri, data, function(data){
            $("#"+plugin+"Form").html(data);
        });
    });

    $("#"+plugin).on("click", ".output_close", function( event ){
        event.preventDefault();
        target = $( event.target );
        div = target.parent().parent();
        div.remove();
    });

    $( "#"+plugin ).on( "click", ".output_history", function( event ){
        event.preventDefault();
        target = $( event.target );
        parent = target.parent().parent();
        id = parent.find( ".hidden" ).attr( "id" );
        data = {"id": id}
        $.download("/download_history", data, "POST")
    } );

    $( "#" + plugin ).on( "click", ".help", function( event ){
        var target = $( event.target );
        var help_content = target.parent().find( ".help_content" );
        help_content.toggle();
    });
}

var addHandlerForFileUploads = function(plugin){
    $("#mast\\.datapower\\."+plugin+"Form").on("change", "input[type='file']",function(event){
        var target = $(event.target);
        var form = $(target.parent());
        var div = form.parent();
        var id = div.attr("id");
        var iframe = div.find("iframe[name^=_"+plugin+"]");
        $(document).trigger("ajaxStart");
        iframe.on("load", function(event){
            $(document).trigger("ajaxStop");
            var value = $.parseJSON($(iframe.contents().children()).find("body").find("pre").html()).filename;
            console.log( "filename: " + value );
            var hidden = $("#mast\\.datapower\\."+plugin+"Form").find("input[type='hidden'][name='"+id+"']");
            hidden.val(value);
        });
        form.trigger("submit");
    });
};

var addHandlerForFormSubmission = function(plugin){
    console.log("Adding handler for plugin " + plugin);
    $("#mast\\.datapower\\."+plugin+"Form").on("click", "#"+plugin+"FormSubmit", function(event){

        console.log("Form submission from " + plugin + "detected");
        var appliances  = [];
        var credentials = [];
        $.each(environment.appliances, function(index, appliance){
            if($("input[type='checkbox'][name='"+appliance.hostname+"']").is(":checked")){
                appliances.push(encodeURIComponent(appliance.hostname));
                credentials.push(encodeURIComponent(xor.encode(appliance.credentials, xor.encode(getCookie("9x4h/mmek/j.ahba.ckhafn"), "_"))));
            }
        });

        target = $(event.target);
        parentForm = target.parent();
        data = 'callable='+encodeURIComponent(parentForm.attr("name")) + '&appliances[]=';
        data += appliances.join('&appliances[]=') + '&credentials[]=';
        data += credentials.join('&credentials[]=');
        parentForm.find("[name]:not([name^=_])").each(function(index, elem){
            elem = $(elem);
            if (elem.attr("type")=="checkbox"){
                data += "&"+elem.attr("name")+"="+elem.is(":checked");
            }else{
                data += "&"+elem.attr("name")+"="+encodeURIComponent(elem.val());
            }
        });

        parentForm.find(".multiTextOuter").each(function(index, elem){
            elem = $(elem);
            id = elem.attr("id");
            selection = elem.find(".multiTextCurrent");
            choices = selection.html().replace("<i>Current selection: </i>", "");
            choices = choices.replace(/<span class="multiTextSelection bordered">/g, "");
            choices = choices.replace(/<span class="multiTextSelectionCancel"> X <\/span><\/span>/g, " ");
            choices = choices.split(" ");
            $.each(choices, function(index, value){
                if (/[a-zA-Z0-9\.]+/.test(value)){
                    data += "&"+encodeURIComponent(id)+"[]="+encodeURIComponent(value);
                }
            });
        });

        parentForm.find(".multiSelectOuter").each(function(index, elem){
            elem = $(elem);
            id = elem.attr("id");
            selection = elem.find(".multiSelectCurrent");
            choices = selection.html().replace("<i>Current selection: </i>", "");
            choices = choices.replace(/<span class="multiSelectSelection bordered">/g, "");
            choices = choices.replace(/<span class="multiSelectSelectionCancel"> X <\/span><\/span>/g, " ");
            choices = choices.split(" ");
            $.each(choices, function(index, value){
                if (/[a-zA-Z0-9\.]+/.test(value)){
                    data += "&"+encodeURIComponent(id)+"[]="+encodeURIComponent(value);
                }
            });
        });

        var uri = plugin;
        console.log("submitting request");
        $.post('/'+uri, data, function(data){
            console.log("Received response");
            console.log("#mast\\.datapower\\."+plugin+"OutputResults");
            $("#mast\\.datapower\\."+plugin+"OutputResults").prepend(data);
        });
    });
};
