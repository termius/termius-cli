#!/usr/bin/env bats


@test "help arg" {
  run serverauditor --help
  [ "$status" -eq 0 ]
}
