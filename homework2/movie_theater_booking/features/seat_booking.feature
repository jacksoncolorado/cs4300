Feature: Seat booking
  Signed-in moviegoers can see per-movie availability and reserve a seat.

  Scenario: View available seats
    Given I am signed in as "Sam"
    And the movie "Dune" has seats "A1" and "A2"
    And seat "A2" is booked for "Dune"
    When I open the seat page for "Dune"
    Then seat "A1" is shown as available
    And seat "A2" is shown as unavailable

  Scenario: Book an available seat
    Given I am signed in as "Sam"
    And the movie "Dune" has available seat "A1"
    When I book seat "A1" for "Dune"
    Then seat "A1" is booked for "Dune" by "Sam" today
    And I see "Seat A1 booked for Dune."
    And seat "A1" is shown as unavailable
