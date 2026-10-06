Feature: Movie listings
  Moviegoers need to see what is showing before booking a seat.

  Scenario: Browse the movie list
    Given the movies "Dune" and "Up" exist
    When I open the movie list page
    Then I see both movies with their descriptions and disabled "Book Now" buttons

  Scenario: No movies showing
    Given no movies exist
    When I open the movie list page
    Then I see "No movies are showing right now" instead of a movie list
