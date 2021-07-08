

$('#delete-topic-btn').click(function () {
  if (confirm('Are you sure you want to delete this topic? All connected apps and articles will be orphaned and inaccessible.')) {
    $("#action").val("delete")
    $('#form1').submit();
  }
})