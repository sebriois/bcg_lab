$(document).ready(function(){
    $('.collapsable h2').click(function(){
      $(".content").toggle();
    });
    
    // Autocomplete widget
    $('.autocomplete').each(function(i){
      var choices = $(this).attr('choices').split(';');
      $(this).autocomplete({
        delay: 0,
        minLength: 2,
        source: choices
      });
    });
    
    $( "#sortable" ).sortable({ 'axis': 'x' });
    
    // Datepicker widget
    $.datepicker.setDefaults( $.datepicker.regional[ "fr" ] );
    
    $( ".datepicker.minDate" ).datepicker({
      dateFormat: 'dd/mm/yy',
      minDate: $('.minDate').attr('min-date')
    });
    $( ".datepicker" ).datepicker({ dateFormat: 'dd/mm/yy' });
    $( ".datepicker.maxToday" ).datepicker({ maxDate: 'today' });
    
    // 
    // EFFECTS
    // 
    $('li.info, li.warning, li.error').effect( 'pulsate', {}, 'slow' );
    $('.expand').hide().click(function(){
        bar = $(this).parent('.bar');
        $(bar).next('.bar_content').show();
        $('.hide', bar).show();
        $(this).hide();
        return false;
    });

    $('.hide').click(function(){
        bar = $(this).parent('.bar');
        $(bar).next('.bar_content').hide();
        $('.expand', bar).show();
        $(this).hide();
        return false;
    });
    
    // FRAIS / REMISES
    var creditFormIsHidden=true;
    var debitFormIsHidden=true;
    
    $('button#credit').click(function(){
      var parent = $(this).parents('.order')[0];
      $('#credit_form', parent).toggle();
      
      creditFormIsHidden = !creditFormIsHidden;
      if(debitFormIsHidden==false){
        $('#debit_form', parent).hide();
        debitFormIsHidden=true;
      }
      
      if(creditFormIsHidden==true && debitFormIsHidden==true){
        $('div#order-buttons', parent).show();
      } else {
        $('div#order-buttons', parent).hide();
      }
    });
    
    $('button#debit').click(function(){
      var parent = $(this).parents('.order')[0];
      $('#debit_form', parent).toggle();
      
      debitFormIsHidden = !debitFormIsHidden;
      if(creditFormIsHidden==false){
        $('#credit_form', parent).hide();
        creditFormIsHidden=true;
      }
      
      if(creditFormIsHidden==true && debitFormIsHidden==true){
        $('div#order-buttons', parent).show();
      } else {
        $('div#order-buttons', parent).hide();
      }
    });
    
    
    // PRODUCT EDIT ALL
    $('input[name="edit_all"]').click(function(){
      $('input.edited_item').prop( "checked", $('input[name="edit_all"]').is(':checked') );
    });
    $('input[name="select_all"]').click(function(){
      $('table.list input[type="checkbox"]').prop( "checked", $(this).is(':checked') );
    });
    
    // 
    // BUTTONS STYLE
    // 
    $("button, .button").not(".no-button").button();
    $(".plus").not(".no-button").button({
      icons: { primary: "ui-icon-plusthick" }
    });
    $(".minus").not(".no-button").button({
      icons: { primary: "ui-icon-minusthick" }
    });
    $(".locked").not(".no-button").button({
      icons: { primary: "ui-icon-locked" }
    });
    $(".unlocked").not(".no-button").button({
      icons: { primary: "ui-icon-unlocked" }
    });
    $(".refresh").not(".no-button").button({
      icons: { primary: "ui-icon-refresh" }
    });
    $(".all").not(".no-button").button({
      icons: { primary: "ui-icon-arrow-2-n-s" }
    });
    $(".pencil").not(".no-button").button({
      icons: { primary: "ui-icon-pencil" }
    });
    $(".key").not(".no-button").button({
      icons: { primary: "ui-icon-key" }
    });
    $(".check").not(".no-button").button({
      icons: { primary: "ui-icon-check" }
    });
    $(".comment").not(".no-button").button({
      icons: { primary: "ui-icon-comment" }
    });
    $(".mail").not(".no-button").button({
      icons: { primary: "ui-icon-mail-closed" }
    });
    $(".trash").not(".no-button").button({
      icons: { primary: "ui-icon-trash" }
    });
    $(".cart").not(".no-button").button({
      icons: { primary: "ui-icon-cart" }
    });
    $(".zoomin").not(".no-button").button({
      icons: { primary: "ui-icon-zoomin" }
    });
    $(".notice").not(".no-button").button({
      icons: { primary: "ui-icon-notice" }
    });
    $(".next-status").not(".no-button").button({
      icons: { primary: "ui-icon-arrowreturnthick-1-e" }
    });
    $(".back").not(".no-button").button({
      icons: { primary: "ui-icon-arrowreturnthick-1-w" }
    });
    $(".import").not(".no-button").button({
      icons: { primary: "ui-icon-arrowthickstop-1-s" }
    });
    $(".export").not(".no-button").button({
      icons: { primary: "ui-icon-arrowthickstop-1-n" }
    });
    $(".notice").not(".no-button").button({
      icons: { primary: "ui-icon-notice" }
    });
    $(".flag").not(".no-button").button({
      icons: { primary: "ui-icon-flag" }
    });
    $(".close-thick").not(".no-button").button({
      icons: { primary: "ui-icon-closethick" }
    });
    $(".disk").not(".no-button").button({
      icons: { primary: "ui-icon-disk" }
    });
    $(".folder-collapsed").not(".no-button").button({
      icons: { primary: "ui-icon-folder-collapsed" }
    });
    $(".document").not(".no-button").button({
      icons: { primary: "ui-icon-document" }
    });
    $(".no-text").not(".no-button").button({
      text: false
    });
    $(".ui-button-icon-only").height(19);
    
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
    
    $( '.setOrderNb' ).click(function(e){
      e.preventDefault();
      var targetUrl = $(this).attr('href');
      
      $( "#setOrderNb" ).dialog({
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
      
      $( "#setOrderNb" ).dialog("open");
    });
    
    // 
    // PRODUCT PAGE - Select quantity when adding to cart
    // 
    
    $('.addToCart').click(function(e){
      if( $(this).parent('td').parent('tr').hasClass('expired') == false ) {
        $('.show_expired_warning').hide();
      } else {
        $('.show_expired_warning').show();
      }
      $('#addToCart.dialog input[name="product_id"]').val($(this).attr('id'));
      $("#addToCart.dialog").dialog('open');
    });
    $('#addToCart.dialog').dialog({
      width: 500,
      buttons: {
        Valider: function() {
          var qty = +( $('input[name="quantity"]').val() );
          var intRegex = /^\d+$/;
          
          if ( intRegex.test(qty) && qty > 0 ) {
            $("#qty-error-msg").text('');
            $( this ).dialog( "close" );
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
    // PRODUCT PAGE - edit list
    // 
    $(".confirm_edit").click(function(e){
      var get_arg = [];
      $('.edited_item:checked').each(function(i){
        get_arg.push($(this).val());
      });
      $('input[name="product_ids"]').attr('value',get_arg.join(","));
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
          "Valider la mise à jour du prix": function() {
            $('input[name="sendChanges"]').val("True");
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
    
    $('.check.csv-import').click(function(){
      $('#sortable li').each(function(i){
        if ( i == 0 ) {
          $('input[name="column_order"]').val( $(this).text() );
        } else {
          var current_val = $('input[name="column_order"]').val();
          $('input[name="column_order"]').val( current_val + ";" + $(this).text() );
        }
      });
    });
    
    $("#confirm_import").click(function(e){
      e.preventDefault();
      
      var targetUrl = $(this).attr('href');
      var get_arg = [];
      
      $('.imported_item:checked').each(function(i){
        get_arg.push($(this).val());
      });
      
      window.location.href = targetUrl + "&items=" + get_arg.join(",");
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
    
    
    
    // 
    //    AJAX REQUESTS
    // 
    
    $('.save-changes').click(function(){
      var parent = $(this).parents('.order')[0];
      
      // SAVE TEAM
      if( $('#select-team', parent).length > 0 ) {
        $.ajax({
          url: $('#select-team', parent).attr('url'),
          async: false,
          data: {
            'team_id': $('#select-team', parent).val()
          },
          error: function(jqXHR, textStatus, errorThrown){
            alert('pb equipe');
            alert(jqXHR.responseText);
          }
        });
      }
      
      // SAVE BUDGET
      if( $('#select-budget', parent).length > 0 ) {
        $.ajax({
          url: $('#select-budget', parent).attr('url'),
          async: false,
          data: {
            'budget_id': $('#select-budget', parent).val()
          },
          error: function(jqXHR, textStatus, errorThrown){
            alert(jqXHR.responseText);
          }
        });
      }
      
      // SAVE QUANTITIES
      $('#setQuantity', parent).each(function(){
        var orderitem_id = $(this).parent('tr').attr('id');
        var qty = +($('input', this).val());
        
        $.ajax({
          url: $('input', this).attr('url'),
          async: false,
          data: {
            'orderitem_id': orderitem_id,
            'quantity': qty
          },
          error: function(jqXHR, textStatus, errorThrown){
            alert(jqXHR.responseText);
          }
        });
      });
      
      // SAVE URGENT & PROBLEM
      var is_urgent = $('#is_urgent', parent).is(':checked');
      var has_problem = $('#has_problem', parent).is(':checked');
      var url_urgent = $('#is_urgent', parent).attr('url');
      var url_problem = $('#has_problem', parent).attr('url');
      
      $.ajax({
        url: url_urgent,
        async: false,
        data: { 'is_urgent': is_urgent },
        error: function(jqXHR, textStatus, errorThrown){
          alert(jqXHR.responseText);
        }
      });
      $.ajax({
        url: url_problem,
        async: false,
        data: { 'has_problem': has_problem },
        error: function(jqXHR, textStatus, errorThrown){
          alert(jqXHR.responseText);
        }
      });
      
      // SAVE ORDER NOTES
      var url_notes = $('textarea', parent).attr('url');
      var notes = $('textarea', parent).val();
      if ( url_notes ) {
        $.ajax({
          url: url_notes,
          async: false,
          data: {
            'notes': notes
          },
          error: function(jqXHR, textStatus, errorThrown){
            alert(jqXHR.responseText);
          }
        });
      }
      
      // SAVE ORDER NUMBER
      var url_order_nb = $('#order_number', parent).attr('url');
      var number = $('#order_number', parent).val();
      
      if ( url_order_nb && number ) {
        $.ajax({
          url: url_order_nb,
          async: false,
          data: {
            'number': number
          },
          error: function(jqXHR, textStatus, errorThrown){
            alert(jqXHR.responseText);
          }
        });
      }
      
      $(parent).effect('highlight');
    });
});
