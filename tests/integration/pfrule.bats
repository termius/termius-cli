#!/usr/bin/env bats

setup() {
    rm ~/.serverauditor.storage || true
}

@test "pfrule help by arg" {
    run serverauditor pfrule --help
    [ "$status" -eq 0 ]
}

@test "pfrule help command" {
    run serverauditor help pfrule
    [ "$status" -eq 0 ]
}

@test "Add local pfrule" {
    host=$(serverauditor host --label test2 --address 127.0.0.1)
    run serverauditor pfrule --local --host $host 2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add remote pfrule" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --remote --host $host 2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add dynamic pfrule" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --dynamic --host $host 2222
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add local pfrule with bound_address" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --local --host $host local:2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add remote pfrule with bound_address" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --remote --host $host localhost:2:127.0.0.1:2222
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add dynamic pfrule with bound_address" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --dynamic --host $host 127.0.0.1:2222
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}


@test "Not add local pfrule with invalid binding" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --local --host $host 127.0.0.1:2222
    [ "$status" -eq 1 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Not add remote pfrule with invalid binding" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --remote --host $host 127.0.0.1:2222
    [ "$status" -eq 1 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Not add dynamic pfrule with invalid binding" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --dynamic --host $host 127.0.0.1:2222.13
    [ "$status" -eq 1 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add remote pfrule require host" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule --remote localhost:2:127.0.0.1:2222
    [ "$status" -eq 1 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add remote pfrule require pf_type" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    run serverauditor pfrule  --host $host  localhost:2:127.0.0.1:2222
    [ "$status" -eq 1 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
