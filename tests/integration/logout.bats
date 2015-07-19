#!/usr/bin/env bats

@test "logout help by arg" {
  run serverauditor logout --help
  [ "$status" -eq 0 ]
}

@test "logout help command" {
  run serverauditor help logout
  [ "$status" -eq 0 ]
}
