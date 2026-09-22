(() => {
  const canvas = document.getElementById('canvas');
  const button = document.getElementById('fullscreen');
  const root = document.documentElement;
  const current = () => document.fullscreenElement || document.webkitFullscreenElement;
  const enter = root.requestFullscreen || root.webkitRequestFullscreen;
  const leave = document.exitFullscreen || document.webkitExitFullscreen;
  const focus = () => canvas.focus({ preventScroll: true });
  if (!enter || !leave) return; // Unsupported browsers retain the fitted game.
  button.hidden = false;
  button.addEventListener('click', async () => {
    try {
      if (current()) await leave.call(document);
      else await enter.call(root); // Direct user gesture; no key binding.
    } catch (error) {
      console.warn('Fullscreen unavailable:', error.message);
      button.title = 'Fullscreen is unavailable in this browser window';
    } finally {
      focus();
    }
  });
  for (const event of ['fullscreenchange', 'webkitfullscreenchange']) {
    document.addEventListener(event, () => {
      button.textContent = current() ? 'Exit fullscreen' : 'Fullscreen';
      button.title = current() ? 'Exit fullscreen (Esc may also pause the game)' : 'Enter fullscreen';
      focus();
    });
  }
  // No global key handler: Escape retains browser exit and existing game pause
  // behavior. The Exit fullscreen button changes only browser presentation.
  // Keyboard activation of the shell button must not also become a game action.
  for (const event of ['keydown', 'keyup']) {
    button.addEventListener(event, (e) => e.stopPropagation());
  }
})();
