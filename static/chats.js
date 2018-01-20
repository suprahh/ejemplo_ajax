$(function (){

    setInterval(function(){
        $.getJSON('/_cargar_charts', function(data) {
       console.log(data);
      }) }, 3000);

})

