var Clock = {
  totalSeconds: Number($('#minutes').text())*60 + Number($('#seconds').text()),
  start: function () {
    
    var self = this;
    function pad(val) { return val > 9 ? val : "0" + val; }
    this.interval = window.setInterval(function () {
      self.totalSeconds += 1;
    
      $('input#countup-min').attr('value', pad(Math.floor(self.totalSeconds / 60 % 60)));
      $('input#countup-sec').attr('value', pad(parseInt(self.totalSeconds % 60)));
    }, 1000);
  },
  
 
  pause: function () {
    clearInterval(this.interval);
    delete this.interval;
    $('input#pauseButton').attr('type', 'hidden');
    $('input#resumeButton').attr('type', 'button');
    $(".pdd-ticket-input").toggleClass('pdd-toggle-pointer-events');
  },

  resume: function () {
    if (!this.interval) this.start();
    $('input#resumeButton').attr('type', 'hidden');
    $('input#pauseButton').attr('type', 'button');
    $(".pdd-ticket-input").toggleClass('pdd-toggle-pointer-events');
  },
  
  
};

       

    $(document).ready(function(){
      // таймер
      // $('#startButton').click(function () { Clock.start(); });
      Clock.start();
      $('#pauseButton').click(function () { Clock.pause(); });
      $('#resumeButton').click(function () { Clock.resume(); });

    // Проверка ответов вопроса
      $(".pdd-check-button").click(function(){

        var checked_groupe = false
        $('.pdd-ticket-input').each(function(){
          if ( $(this).prop( "checked" ) ) {
            checked_groupe = true;
          }
        });

        if (checked_groupe === true) {
          var $questionAnswerBlock = $('.pdd-question-answer-block');
          $questionAnswerBlock.addClass( "pdd-passed-question" );

          $(".pdd-label").each(function(){
            $(this).addClass( "pdd-pass-question" )
          });

          // Показать подсказку если ответ не правильный
          
          if ($('#tip-content').text() !== 'None') {
            if ( $('input[name="choice"]:checked') !== $("input.right-ans") ){
                    $tipContent.addClass('open');
            };
          };
          

          $(".pdd-check-button").css( "display", "none" );
          $(".pdd-next-button").css( "display", "inline-block" );


      // Окраска серых звездочек зеленый/красный
          var checkedInput = $('.pdd-ticket-input:checked');
          var rightChoice = $('input.right-ans');
          var firstGreyStar = $('span.grey-star-1');
          if ( checkedInput.attr('value') === rightChoice.attr('value') ){
            firstGreyStar.attr( 'style', 'color: green' )
          }
          else {
            firstGreyStar.attr('style', 'color: red' )
            // Выпадаэщее сообщение о добавлении 5 доп вопросов на экзамене
            if ( $('.active').find('a').text() === ' Экзамен' &&
              $('.star-line').find('span.glyphicon.glyphicon-star').length < 30 )
             { alert('Вы допустили ошибку, вам будет добавлено 5 дополнительных вопросов.');
            }        
          }
        }
      })

      checkedInputValue = $('.pdd-ticket-input:checked').attr('value');
      rightChoiceValue = $('input.right-ans').attr('value');
      firstGreyStar = $('span.grey-star-1')


// Подсказка
  var $tipTog = $('#tip-tog');
  var $tipContent = $('#tip-content')
  $tipTog.click(function(){
  $tipContent.toggleClass('open');
  })


// Для клика на row темы для прохождения вопросов из темы

$('tr.theme-list-item[data-href]').on("click",function(){
  window.location = $(this).data('href');
  return false;
});
$("td > a").on("click",function(e){
  e.stopPropagation();
});

})