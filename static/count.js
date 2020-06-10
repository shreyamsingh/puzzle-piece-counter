window.onload = function() {
  var str = document.getElementById("pieces").innerHTML;
  var i = 0;
  var num = "";
  var target = document.getElementById("pieces").getAttribute("target");
  function updateCount() {
    const count = +document.getElementById("pieces").innerText;
    if (count < target) {
      document.getElementById("pieces").innerHTML = count + 1;
      setTimeout(updateCount, 3);
    }
    else {
      document.getElementById("pieces").innerHTML = target.bold();
    }
  }
  updateCount();
}
