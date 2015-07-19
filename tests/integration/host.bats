#!/usr/bin/env bats

@test "host help by arg" {
  run serverauditor host --help
  [ "$status" -eq 0 ]
}

@test "host help command" {
  run serverauditor help host
  [ "$status" -eq 0 ]
}
