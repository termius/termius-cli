#!/usr/bin/env bats


@test "groups help by arg" {
    run serverauditor groups --help
    [ "$status" -eq 0 ]
}

@test "groups help command" {
    run serverauditor help groups
    [ "$status" -eq 0 ]
}

@test "List groups in table format" {
    rm ~/.serverauditor.storage || true
    serverauditor group -L 'test group' --port 2 --username 'use r name'
    run serverauditor groups
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "List groups in subgroup in table format" {
    rm ~/.serverauditor.storage || true
    parent=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    serverauditor group -L 'test group' --parent-group $parent --port 2 --username 'use r name'
    run serverauditor groups $parent
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "List groups recursivly in subgroup in table format" {
    rm ~/.serverauditor.storage || true
    grandparent=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    parent=$(serverauditor group -L 'test group' --parent-group $grandparent --port 2 --username 'use r name')
    serverauditor group -L 'test group' --parent-group $parent --port 2 --username 'use r name'
    run serverauditor groups $grandparent
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
