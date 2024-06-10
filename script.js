$(document).ready(function () {
  $("#menuAccordion").on("show.bs.collapse", function () {
    $("#menuAccordion .collapse.show").collapse("hide");
  });
});
