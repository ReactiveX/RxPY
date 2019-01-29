.. _migration:

Migration
=========

* pipe chaining
* time in seconds
* removal of result mapper in zip, zip_with_iterable, join, group_join, combine_latest, with_latest_from
* combine_latest, with_latest_from: starmap operator to ease tuple unpacking.
* removal of using operator ?
* subscription function takes two parameters: observer and scheduler
* merge, zip, combine_latest... take only observable arguments, no lists.