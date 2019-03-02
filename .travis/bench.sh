#!/usr/bin/env bash

# This script runs a subset of unit tests (minus concurrency, which does too
# much hard sleeps to be a useful benchmark) a couple of times, averaging the
# durations as parsed from pytest output.
#
# It does this for each of the branches passed as commandline arguments, plus
# the branch we were on when invoked.

testargs="--cache-clear --ignore=tests/test_concurrency"
rounds=10

git remote add upstream https://github.com/ReactiveX/RxPY.git

git stash | grep "^No"
pop=$?

head=$(git status | head -n 1 | grep -o "[^ ]*$")

for branch in $* $head
do
  echo ""
  if [[ "$branch" != "$head" ]]
  then
    git fetch upstream $branch
    git checkout "upstream/$branch"
  else
    git checkout "$branch"
  fi

  sum=0
  for round in $(seq $rounds)
  do
    echo -n " - Round $round of $rounds"
    sec=$(pytest $testargs | grep -o "passed in .* s")
    ret=$?
    echo -n " | $sec"

    sec=$(echo $sec | sed -e "s/[^0-9]//g")
    sum=$(($sum + $sec))
    avg=$((((($sum * 10) / $round) + 5) / 10))

    echo -n " | total $(echo $sum | sed -e "s/\([0-9]\{2\}\)$/.\1/") s"
    echo -n " | average $(echo $avg | sed -e "s/\([0-9]\{2\}\)$/.\1/") s"

    if [[ $ret == 0 ]]; then echo " | OK"; else echo " | FAIL"; fi
  done
done

if [[ $pop != 0 ]]; then git stash pop; fi
