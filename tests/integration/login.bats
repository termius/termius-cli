#!/usr/bin/env bats

@test "login help by arg" {
  run serverauditor login --help
  [ "$status" -eq 0 ]
}

@test "login help command" {
  run serverauditor help login
  [ "$status" -eq 0 ]
}
