$(document).ready(function(){
    $('fieldset legend').click(function(){
        $(this).parent().toggleClass('collapsed');
        $(this).parent().children(".hide_me").toggle();
    });
    
    // Set ``autocomplete`` widget on fields having class ``autocomplete``
    if ( $('.autocomplete').length > 0 ) {
        var choices = $('.autocomplete').attr('choices').split(';');
        $('.autocomplete').autocomplete(choices, {
            matchContains: "word",
            scroll: true,
            scrollHeight: 300
        });
    }
    
    // In product index page
    $("#submit_filter").click(function(){
        $("form#product_filter").submit();
        return false;
    });
});