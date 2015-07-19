#!/usr/bin/env bats

@test "tags help by arg" {
  run serverauditor tags --help
  [ "$status" -eq 0 ]
}

@test "tags help command" {
  run serverauditor help tags
  [ "$status" -eq 0 ]
}
