#!/usr/bin/env bash

# This script runs a subset of unit tests (minus test_scheduler, which does too
# many hard sleeps to be a useful benchmark) a couple of times, averaging the
# durations as parsed from pytest output.
#
# It does this for a designated reference branch to compare with, and then again
# for the situation we were in when invoked.
#
# If we're running locally, the reference is taken from an commandline arg, or
# or if none is given we just bench-mark the present situation.
#
# When running on Travis CI, the reference will be the targeted branch in the
# case of pull request builds, or default to "master" for push builds.
#
# Note that the script might switch the local git branch. To protect any unsaved
# work when running locally, it does a git stash first, which is popped back
# later.
#
# So if you kill the script before it's done, you may end up in the wrong branch
# and/or you may find your work is stashed!

testargs="--cache-clear --ignore=tests/test_scheduler"
defref="master"
rounds=5

stat=$(git status | head -n 1)
hash=$(git log -1 --format=%H)
head=$(echo "$stat" | grep -o "[^ ]*$")
ref=$1
pop=0

if [[ "$TRAVIS" ]]
then
  # Running on Travis; add explicit remote to upstream repository
  git remote add upstream https://github.com/"$TRAVIS_REPO_SLUG".git

  # Compare versus the PR target branch, if any, or the default ref otherwise
  if [[ "$TRAVIS_PULL_REQUEST" != "false" ]]
  then
    head="$hash"
    ref="$TRAVIS_BRANCH"
  else
    head="$TRAVIS_BRANCH"
    ref="$defref"
  fi

else

  # Running locally: save unsaved work, if any
  if [[ $# != 0 ]]
  then
    git stash | grep "^No"
    pop=$?
    if [[ $pop != 0 ]]
    then
      echo "Note: stashed local unsaved changes, do NOT kill this script!"
    fi
  fi

  # If our head is detached, use the hash so we can jump back correctly
  if [[ $(echo "$stat" | grep -o " detached ") ]]
  then
    head="$hash"
  fi

fi


# If $ref is equal to $head, ignore it
if [[ "$ref" == "$head" ]]
then
  ref=""
fi


# All right, go!
for branch in "$ref" "$head"
do
  if [[ $branch == "" ]]
  then
    continue
  fi

  # Checkout the branch / commit
  echo ""
  echo "Checking out $branch"
  if [[ "$TRAVIS" && "$branch" != "$head" ]]
  then
    git fetch upstream $branch
    git checkout upstream/"$branch"
  else
    git checkout "$branch"
    if [[ $pop != 0 && "$branch" == "$head" ]]
    then
      git stash pop
      echo "Note: restored local unsaved changes."
    fi
  fi

  echo ""
  git status | head -n 1

  # Do one warm-up round, which doesn't count toward the average
  echo -n " - Round 0 (warm-up)"
  sec=$(pytest $testargs | grep -o "passed in .* s")
  ret=$?
  echo -n " | $sec"
  if [[ $ret == 0 ]];
  then
    echo " | OK"
  else
    echo " | FAIL"
    exit $ret
  fi

  # Main loop, run "pytest $testargs" $rounds times
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

    if [[ $ret == 0 ]]
    then
      echo " | OK"
    else
      echo " | FAIL"
      exit $ret
    fi
  done
done
