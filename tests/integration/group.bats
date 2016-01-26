#!/usr/bin/env bats

@test "group help by arg" {
    run serverauditor group --help
    [ "$status" -eq 0 ]
}

@test "group help command" {
    run serverauditor help group
    [ "$status" -eq 0 ]
}

@test "Add general group" {
    rm ~/.serverauditor.storage || true
    run serverauditor group -L 'test group' --port 2 --username 'use r name'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update group" {
    rm ~/.serverauditor.storage || true
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group -L 'test group' --port 2 --username 'user' $group
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update many groups" {
    rm ~/.serverauditor.storage || true
    group1=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group2=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group -L 'test group' --port 2 --username 'user' $group1 $group2
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete group" {
    rm ~/.serverauditor.storage || true
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --delete $group
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete many groups" {
    rm ~/.serverauditor.storage || true
    group1=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group2=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --delete $group1 $group2
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
