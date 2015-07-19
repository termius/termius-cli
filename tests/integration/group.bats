#!/usr/bin/env bats

@test "group help by arg" {
  run serverauditor group --help
  [ "$status" -eq 0 ]
}

@test "group help command" {
  run serverauditor help group
  [ "$status" -eq 0 ]
}
