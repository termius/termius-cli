#!/usr/bin/env bats


@test "info help by arg" {
  run serverauditor info --help
  [ "$status" -eq 0 ]
}

@test "info help command" {
  run serverauditor help info
  [ "$status" -eq 0 ]
}
