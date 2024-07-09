
function toggleTable(year) {
    // Находим таблицу по id
    var table = document.getElementById('table-' + year);

    // Проверяем текущее состояние отображения
    if (table.classList.contains('active')) {
        table.classList.remove('active'); // Если открыта, закрываем
    } else {
        table.classList.add('active'); // Если закрыта, открываем
    }
}