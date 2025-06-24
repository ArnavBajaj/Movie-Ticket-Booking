document.addEventListener("DOMContentLoaded", function () {
    // Populate movies on booking page
    fetchMovies();
});

function fetchMovies() {
    fetch("http://127.0.0.1:5000/movies") // Replace with your backend URL
        .then(response => response.json())
        .then(data => {
            let moviesDropdown = document.getElementById("movie");
            data.forEach(movie => {
                let option = document.createElement("option");
                option.value = movie._id;
                option.textContent = movie.Title;
                moviesDropdown.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching movies:", error));
}
document.getElementById("ticket-booking-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const movieId = document.getElementById("movie").value;
    const showId = document.getElementById("show").value;
    const seats = document.getElementById("seats").value;

    const bookingData = {
        movie_id: movieId,
        show_id: showId,
        no_of_seats: seats,
    };

    fetch("http://127.0.0.1:5000/bookings", { // Replace with your backend URL
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())
    .then(data => {
        alert("Tickets successfully booked! Booking ID: " + data.booking_id);
    })
    .catch(error => console.error("Error booking tickets:", error));
});
