#!/usr/bin/env bats

@test "Identities help by arg" {
  run serverauditor identities --help
  [ "$status" -eq 0 ]
}

@test "Identities help command" {
  run serverauditor help identities
  [ "$status" -eq 0 ]
}

@test "List general identities in table format" {
    rm ~/.serverauditor.storage || true
    serverauditor identity -L local --username 'ROOT' --password 'pa'
    run serverauditor identities
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
