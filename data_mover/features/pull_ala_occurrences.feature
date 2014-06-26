Feature: Pull ALA occurrences using the Data Mover's XMLRPC Service

Scenario: Pull Red Kangaroo occurrences from ALA
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    Then I check if the status of the job is "IN_PROGRESS" for at most 10 seconds
    Then I check if the status of the job is "COMPLETED" for at most 300 seconds
    And I should see "3" files in my temp directory
    And I should see the ALA files in my temp directory

Scenario: Pull an occurrence from ALA that does not exist
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "bad:lsid:here"
    Then I check if the status of the job is "FAILED" for at most 10 seconds
    And I should see "0" files in my temp directory

Scenario: Pull an occurrence from ALA that does not have a common name
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "urn:lsid:biodiversity.org.au:afd.taxon:45ec5b73-1ff7-43dc-9558-43d28b06f107"
    Then I check if the status of the job is "COMPLETED" for at most 100 seconds
    And I should see "3" files in my temp directory
    And I should see the ALA files in my temp directory

