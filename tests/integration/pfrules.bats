#!/usr/bin/env bats

@test "pfrules help by arg" {
  run serverauditor pfrules --help
  [ "$status" -eq 0 ]
}

@test "pfrules help command" {
  run serverauditor help pfrules
  [ "$status" -eq 0 ]
}
