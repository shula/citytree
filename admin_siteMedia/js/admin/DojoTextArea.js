// use dojo's dijit.Editor - a Rich text editor for textarea form elements.

document.write('<script type="text/javascript" src="/admin_media/dojo1.1/dojo/dojo.js" djConfig="parseOnLoad:true, isDebug:true"></script>');
document.write('<script type="text/javascript">dojo.require("dijit.Editor");</script>');

var AddEditor = {
    init: function() {
        var fieldsets = document.getElementsByTagName('fieldset');
        for (var i = 0, fs; fs = fieldsets[i]; i++) {
            var classes = fs.className || fs.getAttribute("class");
            if ( (classes) && (classes.indexOf) && (classes.indexOf("wysiwyg") != -1) ) {
                var textareas = fs.getElementsByTagName('textarea');
                for (var j = 0, ta; ta = textareas[j]; j++) {
                    ta.setAttribute("dojoType", "dijit.Editor");
                }
            }
        }
    },
}


addEvent(window, 'load', AddEditor.init);
