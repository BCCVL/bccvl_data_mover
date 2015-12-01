Feature: Move Service - Downloads from source and moves to destination using the Data Mover's XMLRPC Service

Scenario: Move http://www.intersect.org.au to localhost
    Given I am connected to the Data Mover server
    And I want to use the destination "localhost" and some temp directory
    And my source is "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I check if the status of the job is "COMPLETED" for at most 10 seconds
    And I should see "1" files in my temp directory

Scenario: Using SCP as a source and destination protocol
    Given I am connected to the Data Mover server
    And I want to use the destination "localhost" and some temp directory
    And my source starts with "scp://localhost" and path of some temporary file named "temp_file.txt" with content "this is the content of my temp file"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I check if the status of the job is "COMPLETED" for at most 5 seconds
    And I should see "1" files in my temp directory
    And I should see a file in my temp directory named "temp_file.txt" with content "this is the content of my temp file"

Scenario: Move http://www.intersect.org.au to an unknown destination
    Given I am connected to the Data Mover server
    And I want to use the destination "unknown_destination" and some temp directory
    And my source is "http://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I check if the status of the job is "FAILED" for at most 5 seconds
    And I should see "0" files in my temp directory
    And I should see that the job reason is "[Errno -2] Name or service not known"

Scenario: Move ftp://www.intersect.org.au to localhost - Unknown source type
    Given I am connected to the Data Mover server
    And I want to use the destination "localhost" and some temp directory
    And my source is "ftp://www.intersect.org.au"
    When I request a move with the defined requirements
    Then I should see that the job status is "REJECTED"
    And I should see "0" files in my temp directory
    And I should see that the job reason is "Unknown source URL scheme 'ftp'"

Scenario: Move http://www.intersect.org.a to localhost - Could not download from URL
    Given I am connected to the Data Mover server
    And I want to use the destination "localhost" and some temp directory
    And my source is "http://www.intersect.org.a"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I check if the status of the job is "FAILED" for at most 5 seconds
    And I should see "0" files in my temp directory
    And I should see that the job reason is "[Errno -2] Name or service not known"

Scenario: Move from multiple sources to localhost
    Given I am connected to the Data Mover server
    And I want to use the destination "localhost" and some temp directory
    And my source is of type mixed
    And one of my sources is "http://www.intersect.org.au"
    And one of my sources is "ala://ala?lsid=urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    And one of my sources starts with "scp://localhost" and path of some temporary file named "temp_file.txt" with content "this is the content of my temp file"
    When I request a move with the defined requirements
    Then I should see that the job status is either "PENDING" or "IN_PROGRESS"
    Then I check if the status of the job is "COMPLETED" for at most 300 seconds
    And I should see "5" files in my temp directory
    And I should see a file in my temp directory named "temp_file.txt" with content "this is the content of my temp file"
    And I should see the ALA files in my temp directory

Scenario: Try to move multiple ALA files using the multiple sources
    Given I am connected to the Data Mover server
    And I want to use the destination "localhost" and some temp directory
    And my source is of type mixed
    And one of my sources is "http://www.intersect.org.au"
    And one of my sources is "ala://ala?lsid=urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    And one of my sources is "ala://ala?lsid=urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    When I request a move with the defined requirements
    Then I should see that the job status is "REJECTED"
