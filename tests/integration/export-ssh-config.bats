#!/usr/bin/env bats

@test "export-ssh-config help by arg" {
    run termius import-ssh-config --help
    [ "$status" -eq 0 ]
}

@test "export-ssh-config help command" {
    run termius help import-ssh-config
    [ "$status" -eq 0 ]
}
