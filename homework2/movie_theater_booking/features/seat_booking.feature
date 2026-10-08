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

  Scenario: Seat already taken
    Given I am signed in as "Sam"
    And the movie "Dune" has seats "A1" and "A2"
    And seat "A2" is booked for "Dune"
    When I book seat "A2" for "Dune"
    Then I see "Seat A2 is already booked for Dune."
    And I see a link back to the seat page for "Dune"
    And exactly one booking exists for seat "A2" and "Dune"

  Scenario: Sign in to book a seat
    Given I am not signed in
    And the movie "Dune" has available seat "A1"
    When I open the seat page for "Dune"
    Then I am redirected to sign in before booking

  Scenario: Out-of-service seat is unavailable
    Given I am signed in as "Sam"
    And the movie "Dune" has available seat "A3"
    And seat "A3" is out of service
    When I book seat "A3" for "Dune"
    Then I see "Seat A3 is out of service."
    And no booking exists for seat "A3" and "Dune"
    And seat "A3" is shown as unavailable
