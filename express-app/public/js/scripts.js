function formatDate(dateString) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options).replace(',', '');
}

$(document).ready(function() {
    // Global variable to store search results
    window.results = [];

    $('#searchForm').on('submit', function(e) {
        e.preventDefault();
        var query = $(this).serialize();
        $.get('/search?' + query, function(data) {
            // Update global results variable
            window.results = data;

            // var results = data;
            var tableBody = $('#resultsTable tbody');
            tableBody.empty();
            window.results.forEach(function(log) {
                var row = '<tr>' +
                          '<td>' + log.ID + '</td>' +
                          '<td>' + log.HOST_NAME + '</td>' +
                          '<td>' + log.HOST_IP + '</td>' +
                          '<td>' + log.SYSTEM_TYPE + '</td>' +
                          '<td>' + log.LEVEL + '</td>' +
                          '<td>' + log.PROCESS_NAME + '</td>' +
                          '<td>' + log.CONTENT + '</td>' +
                          '<td>' + formatDate(log.LOG_TIME) + '</td>' +
                        //   '<td>' + log.TIMESTAMP + '</td>' +
                          '</tr>';
                tableBody.append(row);
            });
        });
    });
});

document.getElementById('downloadCsvBtn').addEventListener('click', () => {
    console.log('Download button clicked');
    
    // Assuming `results` is a global variable containing the search results
    if (!window.results || window.results.length === 0) {
        console.log('No results to download');
        alert('No results to download');
        return;
    }

    const rows = [['ID', 'Host Name', 'Host IP', 'System Type', 'Log Level', 'Process Name', 'Content', 'Log Time']];

    window.results.forEach(result => {
        rows.push([
            result.ID,
            result.HOST_NAME,
            result.HOST_IP,
            result.SYSTEM_TYPE,
            result.LEVEL,
            result.PROCESS_NAME,
            result.CONTENT.replaceAll('#', '*').replaceAll(',', '/'), //將特殊字元改為其他代號才能寫進.csv檔案
            formatDate(result.LOG_TIME)
        ]);
    });

    // let txtContent = "data:text/plain;charset=utf-8,\ufeff";
    let csvContent = "data:text/csv;charset=utf-8,\ufeff";

    // rows.forEach(rowArray => {
    //     let row = rowArray.join("\t"); // 使用 tab 作為分隔符
    //     txtContent += row + "\n";
    //   });

    rows.forEach(rowArray => {
        let row = rowArray.join(",");
        csvContent += row + "\r\n";
    });

    // // 双引号包裹： 将整个行用双引号包裹，确保字段中的逗号和引号被正确处理。
    // rows.forEach(rowArray => {
    //     let row = rowArray.map(item => `"${item}"`).join(",");
    //     // csvContent += `"${row}"\r\n`;
    //     csvContent += row + "\r\n";
    // });


    // console.log('CSV content prepared');
    // console.log(csvContent);

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "log_search_results.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link); // Cleanup
});

document.getElementById('modeToggleBtn').addEventListener('click', () => {
    const body = document.body;
    const modeToggleBtn = document.getElementById('modeToggleBtn');
    body.classList.toggle('dark-mode');

    if (body.classList.contains('dark-mode')) {
        modeToggleBtn.textContent = 'Light Mode';
    } else {
        modeToggleBtn.textContent = 'Dark Mode';
    }
});

// 添加一些 CSS 樣式來支援 Dark Mode
const style = document.createElement('style');
style.textContent = `
    .dark-mode {
        background-color: #121212;
        color: #ffffff;
    }
    .dark-mode .form-control {
        background-color: #333333;
        color: #ffffff;
    }
    .dark-mode .btn-primary {
        background-color: #555555;
        border-color: #555555;
    }
    .dark-mode .btn-secondary {
        background-color: #999999;
        border-color: #999999;
    }
    .dark-mode .table-striped {
        background-color: #333333;
        color: #ffffff;
    }
`;
document.head.append(style);
