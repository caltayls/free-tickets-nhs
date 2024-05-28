
const container = document.querySelector("#table-container");
const p = document.createElement('p');

const eventTable = document.createElement('table');



fetch("./new_events.json")
    .then(response => response.json())
    .then(json => json.data)
    .then(dataArray => {
        const tableHeaderRow = document.createElement('tr');
        const columnNames = Object.keys(dataArray[0]);
        columnNames.forEach(name => {
            const tableData = document.createElement('th');
            tableData.innerHTML = name;
            tableHeaderRow.appendChild(tableData);

            });
        eventTable.appendChild(tableHeaderRow);
        container.appendChild(eventTable);

        dataArray.forEach(event => {
            const eventRow = document.createElement('tr');
            // console.log(Object.entries(event))
            Object.entries(event).forEach(([key, value]) => {
                const td = document.createElement('td');
                td.classList.add(key);
                td.innerHTML = value;
                eventRow.appendChild(td);
                
            })
            eventTable.appendChild(eventRow);

        
    });

});