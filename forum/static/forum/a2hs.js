let deferredPrompt;

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/static/forum/serviceWorker.js', {
        scope: '.'
    });
  });
}

window.addEventListener('beforeinstallprompt', (e) => {

  e.preventDefault();
  
  deferredPrompt = e;

  deferredPrompt.prompt();

  deferredPrompt.userChoice
    .then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {

        console.log('Kisan successfully added to home screen.Enjoy the experience !');
      }

      deferredPrompt = null;
    });

});



