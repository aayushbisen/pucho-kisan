let deferredPrompt;
const add_buttons = $(".add_to_home_screen");

window.addEventListener('beforeinstallprompt', (e) => {

  e.preventDefault();
  
  deferredPrompt = e;

  add_buttons.removeClass("hide");

});



add_buttons.click(function () {
  
  deferredPrompt.prompt();

  deferredPrompt.userChoice
    .then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') 
      {
        // Removing the buttons
        add_buttons.remove();
      }

      deferredPrompt = null;
    });

  })


