#!/usr/bin/env bats


@test "hosts help by arg" {
  run serverauditor hosts --help
  [ "$status" -eq 0 ]
}

@test "hosts help command" {
  run serverauditor help hosts
  [ "$status" -eq 0 ]
}
