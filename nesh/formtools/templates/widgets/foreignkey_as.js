YAHOO.nesh.admin.autoselect = function(field, ds, id_no, fnformat) {
    YAHOO.nesh.admin.[field + '_autocomplete'] = function() {
        oACDS = ds;
        oACDS.maxCacheEntries = 60;
        oACDS.queryMatchSubset = true;
        
        // Instantiate first AutoComplete
        oAC = new YAHOO.widget.AutoComplete('AC_{{ FORM_field.field_name }}', 'CON_{{ FORM_field.field_name }}', oACDS);
        oAC.queryDelay = 0.2;
        oAC.forceSelection = true;
        oAC.typeAhead = true;
        
        oAC.formatResult = function(oResultItem, sQuery) {
            format(oResultItem, sQuery);
        }
        $log('created', 'info', 'YAHOO.nesh.admin.'+ field + '_autocomplete']);
    }
    // save params
    YAHOO.nesh.admin.[field + '_autocomplete'].ds = ds;
    YAHOO.nesh.admin.[field + '_autocomplete'].id_no = id_no;
    YAHOO.nesh.admin.[field + '_autocomplete'].fnformat = fnformat;
    
    YAHOO.util.Event.addListener(window, 'load', YAHOO.nesh.admin.[field + '_autocomplete']);
}