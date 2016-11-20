#!/usr/bin/env bats


@test "help arg" {
    run termius --help
    [ "$status" -eq 0 ]
}
