#!/usr/bin/env bats

@test "Identity help by arg" {
    run serverauditor identity --help
    [ "$status" -eq 0 ]
}

@test "Identity help command" {
    run serverauditor help identity
    [ "$status" -eq 0 ]
}

@test "Add general identity" {
    rm ~/.serverauditor.storage || true
    run serverauditor identity -L local --username 'ROOT' --password 'pa'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update identity" {
    rm ~/.serverauditor.storage || true
    identity=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity -L local --username 'ROOT' --password 'pa' $identity
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update many identities" {
    rm ~/.serverauditor.storage || true
    identity1=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    identity2=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity -L local --username 'ROOT' --password 'pa' $identity1 $identity2
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete identity" {
    rm ~/.serverauditor.storage || true
    identity=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity --delete $identity
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete many identities" {
    rm ~/.serverauditor.storage || true
    identity1=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    identity2=$(serverauditor identity -L local --username 'ROOT' --password 'pa')
    run serverauditor identity --delete $identity1 $identity2
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
