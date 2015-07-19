#!/usr/bin/env bats

@test "use help by arg" {
  run serverauditor use --help
  [ "$status" -eq 0 ]
}

@test "use help command" {
  run serverauditor help use
  [ "$status" -eq 0 ]
}
