



  $(document).ready(function() {
  
    $(".analyze").click(function(){
        //analyze
        $("#chosenCity").val( $(".selectedCity").val() );
        $(".downloadInputDirectory").click()
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
    
        
