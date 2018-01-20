$(function (){

    setInterval(function(){
        $.getJSON('/_saludar', function(data) {
       console.log(data);
      }) }, 3000);

})

