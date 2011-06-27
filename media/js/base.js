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

    $( ".datepicker" ).datepicker({ dateFormat: 'dd/mm/yy' });
    $( ".datepicker.maxToday" ).datepicker({ maxDate: 'today' });
    
    // 
    // EFFECTS
    // 
    $('li.info, li.warning, li.error').effect( 'pulsate', {}, 'slow' );
    
    // 
    // BUTTONS STYLE
    // 
    $("button, .button").button();
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
    $(".mail").button({
      icons: { primary: "ui-icon-mail-closed" }
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
    $(".next-status").button({
      icons: { primary: "ui-icon-arrowreturnthick-1-e" }
    });
    $(".back").button({
      icons: { primary: "ui-icon-arrowreturnthick-1-w" }
    });
    $(".import").button({
      icons: { primary: "ui-icon-arrowthickstop-1-s" }
    });
    $(".export").button({
      icons: { primary: "ui-icon-arrowthickstop-1-n" }
    });
    
    // 
    // DIALOGS
    // 
    $('.dialog').dialog({
      autoOpen:       false,
      resizable:      false,
      modal:          true,
      closeOnEscape:  false,
      open: function() {
        $("#loadingDialog").dialog('close');
        $(".ui-dialog-titlebar-close").hide();
      },
      close: function() {
        $("#loadingDialog").dialog('close');
      }
    });
    
    $('.dialog form input').keydown(function (e) {
      if (e.which == 13) {
        // $(this).parent('form').submit();
        return false;
      }
    });
    
    $('a, button').not('.noloading').click(function(e){
      $('#loadingDialog').dialog('open');
    });
    
    $("#loadingDialog").dialog({
      autoOpen:   false,
      resizable:  false,
      modal:      true,
      width:      156,
      open: function(event, ui) {
        $('#loadingDialog').prev('.ui-dialog-titlebar').hide();
        $('#loadingDialog').css({
          'min-height': '30px',
          width: '130px'
        });
        $('#loadingDialog').parent('.ui-dialog').css({
          border: 'none'
        });
      }
    });
    
    
    // 
    // CONFIRMATION DIALOG - create the appropriate content in HTML code
    // 
    $( '.confirm' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#confirm.dialog" ).dialog({
        buttons: {
          Confirmer: function() {
            $( this ).dialog( "close" );
            window.location.href = targetUrl;
          },
          Annuler: function() {
            $('#loadingDialog').dialog('close');
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#confirm.dialog" ).dialog('open');
    });
    
    // 
    // CONFIRMATION DIALOG for deletion
    // 
    $( '.confirmDel' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#confirmDel" ).dialog({
        buttons: {
          Confirmer: function() {
            $( this ).dialog( "close" );
            window.location.href = targetUrl;
          },
          Annuler: function() {
            $('#loadingDialog').dialog('close');
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#confirmDel" ).dialog('open');
    });

    $( '.confirmDelCart' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#confirmDelCart" ).dialog({
        buttons: {
          Confirmer: function() {
            $( this ).dialog( "close" );
            window.location.href = targetUrl;
          },
          Annuler: function() {
            $('#loadingDialog').dialog('close');
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#confirmDelCart" ).dialog('open');
    });
    
    
    // 
    // SECRETARY DIALOGS - delivery date + order nb
    // 
    $( '.setDeliveryDate' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#setDeliveryDate" ).dialog({
        width: 430,
        buttons: {
          Valider: function() {
            var delivery_date = $(".datepicker").val();
            $(this).dialog('close');
            window.location.href = targetUrl + "?delivery_date=" + delivery_date;
          },
          Annuler: function() {
            $('#loadingDialog').dialog('close');
            $(this).dialog('close');
          }
        }
      });
      
      $( "#setDeliveryDate" ).dialog("open");
    });
    
    $( '.setOrderRef' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#setOrderRef" ).dialog({
        width: 430,
        buttons: {
          Valider: function() {
            var number = $('input[name="number"]').val();
            $(this).dialog('close');
            window.location.href = targetUrl + "?number=" + number;
          },
          Annuler: function() {
            $('#loadingDialog').dialog('close');
            $(this).dialog('close');
          }
        }
      });
      
      $( "#setOrderRef" ).dialog("open");
    });
    
    $("#addDebit").dialog({
      width: 400,
      buttons: {
        Valider: function() {
          $('#addDebit input[name="price"]').val($('#addDebit input[name="price"]').val().replace(',','.'));
          $( this ).dialog( "close" );
          $('#loadingDialog').dialog('open');
          $('#addDebit form').submit();
        },
        Annuler: function() {
          $('#loadingDialog').dialog('close');
          $(this).dialog('close');
        }
      }
    });
    $( '.addDebit' ).click(function(e){
      $("#addDebit").dialog('open');
    });
    
    $("#addCredit").dialog({
      width: 400,
      buttons: {
        Valider: function() {
          $('#addCredit input[name="price"]').val($('#addCredit input[name="price"]').val().replace(',','.'));
          $( this ).dialog( "close" );
          $('#loadingDialog').dialog('open');
          $('#addCredit form').submit();
        },
        Annuler: function() {
          $('#loadingDialog').dialog('close');
          $(this).dialog('close');
        }
      }
    });
    $( '.addCredit' ).click(function(e){
      $("#addCredit").dialog('open');
    });
    // 
    // PRODUCT PAGE - Select quantity when adding to cart
    // 
    
    $('.addToCart').click(function(e){
      $('#addToCart.dialog input[name="product_id"]').val($(this).attr('id'));
      $("#addToCart.dialog").dialog('open');
    });
    $('#addToCart.dialog').dialog({
      width: 400,
      buttons: {
        Valider: function() {
          var qty = +( $('input[name="quantity"]').val() );
          var intRegex = /^\d+$/;
          
          if ( intRegex.test(qty) && qty > 0 ) {
            $("#qty-error-msg").text('');
            $( this ).dialog( "close" );
            $('#loadingDialog').dialog('open');
            $('#addToCart.dialog form').submit();
          }
          else {
            $("#qty-error-msg").text("Veuillez saisir une quantité entière positive.");
            $("#qty-error-msg").addClass("warning");
          }
        },
        Annuler: function() {
          $('#loadingDialog').dialog('close');
          $(this).dialog('close');
        }
      }
    });
    
    
    // 
    // CART PAGE - Set quantity dialog
    // 
    $(".setQty").click(function(e){
      $('#setQty.dialog input[name="orderitem_id"]').val($(this).attr('id'));
      $('#setQty.dialog input[name="quantity"]').val( $.trim($(this).text()) );
      $("#setQty.dialog").dialog('open');
    });
    $("#setQty.dialog").dialog({
      width: 400,
      buttons: {
        Valider: function() {
          var qty = $('#setQty.dialog input[name="quantity"]').val();
          var intRegex = /^\d+$/;
          
          if ( intRegex.test(qty) && qty > 0 && qty == parseInt(qty) ) {
            $("#qty-error-msg").text('');
            $( this ).dialog( "close" );
            $('#loadingDialog').dialog('open');
            $('#setQty.dialog form').submit();
          }
          else {
            $("#qty-error-msg").text("Veuillez saisir une quantité entière positive.");
            $("#qty-error-msg").addClass("warning");
          }
        },
        Annuler: function() {
          $('#loadingDialog').dialog('close');
          $(this).dialog('close');
        }
      }
    });
    
    $('.setBudget').click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#setBudget.dialog" ).dialog({
        width: 400,
        buttons: {
          Valider: function() {
            var choice = $('select[name="budget"] option:selected').val();
            
            $( this ).dialog( "close" );
            window.location.href = targetUrl + "?budget=" + parseInt(choice);
          },
          Annuler: function() {
            $('#loadingDialog').dialog('close');
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#setBudget.dialog" ).dialog('open');
    });
    
    $('.sendChanges').click(function(e){
      e.preventDefault();
      
      $("#sendChanges.dialog").dialog({
        width: 800,
        buttons: {
          "Envoyer (Modification permanente)": function() {
            $('input[name="sendChanges"]').val("True");
            $( this ).dialog( "close" );
            $('#loadingDialog').dialog('open');
            $('#productUpdateForm').submit();
          },
          "Ne pas envoyer (Modification exceptionnelle)": function() {
            $('input[name="sendChanges"]').val("False");
            $( this ).dialog( "close" );
            $('#loadingDialog').dialog('open');
            $('#productUpdateForm').submit();
          },
          "Annuler": function() {
            $('#loadingDialog').dialog('close');
            $( this ).dialog( "close" );
          }
        }
      });
      
      $('#sendChanges').dialog("open");
    });

    // 
    // PROVIDER PAGE
    // 
    $('.notesDialog').click(function(e){
      e.preventDefault();
      $('#dialog_content').text( $(this).attr("content") );
      $('#dialog').dialog('open');
    });

    $('.mail').click(function(e){
      $('#mail.dialog input[name="to"]').val($(this).attr('to'));
      $("#mail.dialog").dialog('open');
    });
    $('#mail.dialog').dialog({
      width: 600,
      buttons: {
        Valider: function() {
          $( this ).dialog( "close" );
          $('#loadingDialog').dialog('open');
          $('#mail.dialog form').submit();
        },
        Annuler: function() {
          $('#loadingDialog').dialog('close');
          $(this).dialog('close');
        }
      }
    });

    // 
    // TEAM PAGE - For changing user's team membership
    // 
    $('.setTeam').click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#setTeamDialog" ).dialog({
        width: 400,
        buttons: {
          Valider: function() {
            var team = $('select[name="team_id"]').val();
            $( this ).dialog( "close" );
            window.location.href = targetUrl + "?team_id=" + team;
          },
          Annuler: function() {
            $('#loadingDialog').dialog('close');
            $( this ).dialog( "close" );
          }
        }
      });
      
      $( "#setTeamDialog" ).dialog('open');
    });
});
