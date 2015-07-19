#!/usr/bin/env bats

@test "pull help by arg" {
  run serverauditor pull --help
  [ "$status" -eq 0 ]
}

@test "pull help command" {
  run serverauditor help pull
  [ "$status" -eq 0 ]
}
