Feature: Pull ALA occurrences using the Data Mover's XMLRPC Service

Scenario: Pull Red Kangaroo occurrences from ALA
    Given I am connected to the Data Mover server
    When I pull occurrences from ALA using the LSID "urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae"
    When I check the status of the pull job
    Then I should see that the job status is "DOWNLOADING"
    Then I wait 1 minutes
    When I check the status of the pull job
    Then I should see that the job status is "COMPLETE"
    Then I should see the file "behave_test/ALA/urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae.csv"
    Then I should see the file "behave_test/ALA/urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae.json"
