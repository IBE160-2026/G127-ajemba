// Moves keyboard focus to the part heading when a link such as "#part-2" is followed (EXPERIENCE.md).
(function () {
  function focusPart() {
    var id = window.location.hash.slice(1);
    if (!/^part-\d+$/.test(id)) { return; }
    var heading = document.getElementById(id);
    if (heading) { heading.focus(); }
  }
  window.addEventListener("hashchange", focusPart);
  focusPart();
})();
