



  $(document).ready(function() {
  
    $(".analyze").click(function(){
        //analyze
        $(".alert").removeClass("hideMe");
        setTimeout(function(){
          $("#chosenCity").val( $(".selectedCity").val() );
          $(".downloadInputDirectory").click()
        },2000)
        
        });

   $(".deleteUser").click(function(){
        var name=$(this).parent().prev().prev().text();
        var email = $(this).parent().prev().text();
        $('#firstName').val(name);
        $('#email').val(email);
        $(".performDelete").click();
        //$()
        //console.log( ($(this).parent().prev().text()  )  )
     
        
        });
        
    
    });
    
        
