// On logout, remove everything the browser kept for the signed-in user (AD-19.3):
// every localStorage key starting with "recall:" (the essay draft backup) and "htmx-history-cache".
// This runs when the logout form is submitted, before the browser sends the POST.
(function () {
  var PREFIXES = ["recall:", "htmx-history-cache"];

  function clearRecallStorage() {
    try {
      var keys = [];
      for (var i = 0; i < localStorage.length; i++) {
        keys.push(localStorage.key(i));
      }
      keys.forEach(function (key) {
        if (PREFIXES.some(function (prefix) { return key.indexOf(prefix) === 0; })) {
          localStorage.removeItem(key);
        }
      });
    } catch (e) {
      // Storage can be blocked by the browser; the logout must still go ahead.
    }
  }

  document.addEventListener("submit", function (event) {
    if (event.target && event.target.hasAttribute("data-recall-logout")) {
      clearRecallStorage();
    }
  });
})();
