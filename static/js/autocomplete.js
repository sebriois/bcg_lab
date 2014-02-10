$(document).ready(function(){
    suggestions = function( jquery_elem, appendTo ){
       options = {
            appendTo: appendTo,
            minChars: 3,
            maxHeight: 300,
            zIndex: 9999,
            deferRequestBy: 0 //miliseconds
       };
       url = $(jquery_elem).attr('autocomplete_url');
       choices = $(jquery_elem).attr('choices');
       if( url ) {
           options['serviceUrl'] = url;
       }
       else {
           if( choices ) {
               options['lookup'] = choices.split(';');
           }
       }
       $(jquery_elem).autocomplete(options);
    };
    
    init_suggestions = function() {
        $('.autocomplete').each( function(i) {
            var position       = $(this).offset();
            var height         = $(this).height();
            var padding_top    = parseInt($(this).css('padding-top'));
            var padding_bottom = parseInt($(this).css('padding-bottom'));
            var margin_top     = parseInt($(this).css('margin-top'));
            var margin_bottom  = parseInt($(this).css('margin-bottom'));
            var margin_left    = parseInt($(this).css('margin-left'));

            var suggestions_container = $('<div/>')
                .attr('id', "suggestion-" + String(i))
                .css({
                    'position': 'absolute',
                    'top': String(position.top + height + padding_top + padding_bottom + margin_top + margin_bottom ) + 'px',
                    'left': String(position.left + margin_left) + 'px'
                });
            $(this).after(suggestions_container);
            suggestions( $(this), suggestions_container );
        });
    };
    
    init_suggestions();
});