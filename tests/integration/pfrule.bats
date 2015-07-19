#!/usr/bin/env bats

@test "pfrule help by arg" {
  run serverauditor pfrule --help
  [ "$status" -eq 0 ]
}

@test "pfrule help command" {
  run serverauditor help pfrule
  [ "$status" -eq 0 ]
}
