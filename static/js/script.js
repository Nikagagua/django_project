// Show More Topics
const showMoreTopicsButton = document.getElementById('showMoreTopics');
const additionalTopics = document.getElementById('additionalTopics');

if (showMoreTopicsButton && additionalTopics) {
    showMoreTopicsButton.addEventListener('click', function (event) {
        event.preventDefault();
        additionalTopics.style.display = 'block';
        showMoreTopicsButton.style.display = 'none';
    });
}

// Show More Rooms
const showMoreRoomsButton = document.getElementById('showMoreRooms');
const additionalRooms = document.getElementById('additionalRooms');

if (showMoreRoomsButton && additionalRooms) {
    showMoreRoomsButton.addEventListener('click', function (event) {
        event.preventDefault();
        additionalRooms.style.display = 'block';
        showMoreRoomsButton.style.display = 'none';
    });
}
