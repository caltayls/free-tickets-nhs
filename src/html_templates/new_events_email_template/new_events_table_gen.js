fetch('./new_events.json')
  .then(response => response.json())
  .then(data => {
    // Work with the loaded JSON data
    console.log(data);
  })

