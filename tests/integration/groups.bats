#!/usr/bin/env bats


@test "groups help by arg" {
  run serverauditor groups --help
  [ "$status" -eq 0 ]
}

@test "groups help command" {
  run serverauditor help groups
  [ "$status" -eq 0 ]
}
