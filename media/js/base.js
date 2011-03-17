$(document).ready(function(){
  $('.collapsable h2').click(function(){
    $(".content").toggle();
    $('.ui-icon-arrowthickstop-1-n').toggleClass('ui-icon-arrowthickstop-1-s');
  });
  
    // Autocomplete widget
    if ( $('#autocomplete').length > 0 ) {
        var choices = $('#autocomplete').attr('choices').split(';');
        $('#autocomplete').autocomplete({
          delay: 0,
          minLength: 2,
          source: choices
        });
    }
    
    // Datepicker widget
    $.datepicker.setDefaults( $.datepicker.regional[ "fr" ] );
    
    $( ".datepicker" ).datepicker({
      dateFormat: 'dd/mm/yy',
      maxDate: 'today'
    });
    
    // 
    // EFFECTS
    // 
    function effectCallback() {
      setTimeout(function() {
        $('li.info').effect('blind', {}, '2000', function() { 
          $(this).hide() 
        });
      }, 1000 );
    };
    
    $('li.info, li.warn, li.error').effect( 
      'pulsate', {}, 'slow', effectCallback
    );
    
    // 
    // BUTTONS STYLE
    // 
    $(".button").button();
    $(".plus").button({
      icons: { primary: "ui-icon-plusthick" }
    });
    $(".minus").button({
      icons: { primary: "ui-icon-minusthick" }
    });
    $(".locked").button({
      icons: { primary: "ui-icon-locked" }
    });
    $(".unlocked").button({
      icons: { primary: "ui-icon-unlocked" }
    });
    $(".refresh").button({
      icons: { primary: "ui-icon-refresh" }
    });
    $(".all").button({
      icons: { primary: "ui-icon-arrow-2-n-s" }
    });
    $(".pencil").button({
      icons: { primary: "ui-icon-pencil" }
    });
    $(".key").button({
      icons: { primary: "ui-icon-key" }
    });
    $(".check").button({
      icons: { primary: "ui-icon-check" }
    });
    $(".comment").button({
      icons: { primary: "ui-icon-comment" }
    });
    $(".trash").button({
      icons: { primary: "ui-icon-trash" }
    });
    $(".cart").button({
      icons: { primary: "ui-icon-cart" }
    });
    $(".zoomin").button({
      icons: { primary: "ui-icon-zoomin" }
    });
    $(".notice").button({
      icons: { primary: "ui-icon-notice" }
    });
    
    // 
    // DIALOGS
    // 
    
    $('#dialog').dialog({
      autoOpen: false,
      resizable: false,
      modal: true
    });
    $('#dialog-date').dialog({
      autoOpen: false,
      resizable: false,
      modal: true
    });
    $('#dialog-qty').dialog({
      autoOpen: false,
      resizable: false,
      modal: true
    });
    
    $('#dialog-confirm').dialog({
      autoOpen: false,
      resizable: false,
      modal: true
    });
        
    $('#dialog-confirm-del').dialog({
      autoOpen: false,
      resizable: false,
      modal: true
    });
    
    // 
    // CONFIRMATION DIALOG - create the appropriate content in HTML code
    // 
    
    $( '.confirmDialog' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#dialog-confirm" ).dialog({
        buttons: {
          Confirmer: function() {
            $( this ).dialog( "close" );
            window.location.href = targetUrl;
          },
          Annuler: function() {
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#dialog-confirm" ).dialog('open');
    });
    
    // 
    // CONFIRMATION DIALOG for deletion
    // 
    
    $( '.confirmDialogDel' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#dialog-confirm-del" ).dialog({
        buttons: {
          Confirmer: function() {
            $( this ).dialog( "close" );
            window.location.href = targetUrl;
          },
          Annuler: function() {
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#dialog-confirm-del" ).dialog('open');
    });
    
    // 
    // DATE DIALOG
    // 
    $( '.dateDialog' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#dialog-date" ).dialog({
        width: 430,
        buttons: {
          Valider: function() {
            var delivery_date = $(".datepicker").val();
            $(this).dialog('close');
            window.location.href = targetUrl + "?delivery_date=" + delivery_date;
          },
          Annuler: function() {
            $(this).dialog('close');
          }
        }
      });
      
      $( "#dialog-date" ).dialog("open");
    });
    
    // 
    // PRODUCT PAGE - Select quantity form
    // 
    
    $( '.quantityDialog' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#dialog-qty" ).dialog({
        buttons: {
          Valider: function() {
            var url = targetUrl.split("1?"); // 1 being the default qty
            var args = "";
            var qty = $('input[name="quantity"]').val();
            
            if ( parseInt(qty) > 0 ) {
              if ( url.length > 1 ) {
                args = url[1];
              }
              $( this ).dialog( "close" );
              window.location.href = url[0] + qty + "?" + args;
            }
            else {
              alert( "Merci de saisir une quantité > 0" );
            }
          },
          Annuler: function() {
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#dialog-qty" ).dialog('open');
    });
    
    // 
    // CART PAGE - Set quantity dialog
    // 
    
    $( '.setQtyDialog' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      $('input[name="quantity"]').val( parseInt($(this).text()) );
      
      $( "#dialog-qty" ).dialog({
        buttons: {
          Valider: function() {
            var url = targetUrl.split("/0"); // 0 being the default qty
            var qty = $('input[name="quantity"]').val();
            
            if ( parseInt(qty) > 0 ) {
              $( this ).dialog( "close" );
              window.location.href = url[0] + "/" + qty;
            }
            else {
              alert( "Merci de saisir une quantité > 0" );
            }
          },
          Annuler: function() {
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#dialog-qty" ).dialog('open');
    });
    
    // 
    // PROVIDER PAGE - Dialog that displays notes
    // 
    $('.notesDialog').click(function(e){
      e.preventDefault();
      $('#dialog_content').text( $(this).attr("content") );
      $('#dialog').dialog('open');
    });
});
