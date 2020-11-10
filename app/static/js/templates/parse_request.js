$(document).ready(function () {
$('#result_table').DataTable({
"paging": false,
"searching": true,
"rowsGroup": [0],
"order": [[ 0, "desc" ]]
});
$('.dataTables_length').addClass('bs-select');
});


